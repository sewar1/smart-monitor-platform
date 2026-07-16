package com.sewarl.smartmonitor.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * Security Filter that intercepts every inbound HTTP request exactly once.
 * Replaces Flask's custom @token_required decorator to secure REST endpoints.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(
        @NonNull HttpServletRequest request,
        @NonNull HttpServletResponse response,
        @NonNull FilterChain filterChain
    ) throws ServletException, IOException {
        
        final String authHeader = request.getHeader("Authorization");
        final String jwt;
        final String username;

        // 1. Guard Clause: Skip filtering if Authorization header is missing or does not start with Bearer
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        // Extract the raw token string from the header value (skipping "Bearer ")
        jwt = authHeader.substring(7);
        
        try {
            username = jwtService.extractUsername(jwt);

            // 2. If token contains a valid username and the current security context is not already authenticated
            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                // Fetch fresh user details from our relational database
                UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);

                // 3. Validate token integrity against database records
                if (jwtService.isTokenValid(jwt, userDetails)) {
                    UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                            userDetails,
                            null,
                            userDetails.getAuthorities()
                    );
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    
                    // Register the authenticated user context inside Spring Security
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                    log.debug("Successfully authenticated user: {} via JWT", username);
                }
            }
        } catch (Exception e) {
            log.error("Failed to parse or validate JWT token: {}", e.getMessage());
        }

        // 4. Pass the request downstream to the next filter in the chain
        filterChain.doFilter(request, response);
    }
}