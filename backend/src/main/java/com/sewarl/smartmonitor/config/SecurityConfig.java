package com.sewarl.smartmonitor.config;

import java.util.Arrays;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import com.sewarl.smartmonitor.repository.UserRepository;

/**
 * Enterprise Security Configuration for the Smart Monitor backend.
 * Handles stateless JWT authentication, password encryption via BCrypt, 
 * CORS policies, and fine-grained URL-based authorization rules.
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity // Enabled to support method-level security via @PreAuthorize across controllers/services
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;

    /**
     * Constructor injection with @Lazy annotation.
     * Prevents circular dependency issues between SecurityConfig, JwtAuthenticationFilter, 
     * and security-related beans during Spring container initialization.
     */
    public SecurityConfig(@Lazy JwtAuthenticationFilter jwtAuthFilter) {
        this.jwtAuthFilter = jwtAuthFilter;
    }

    /**
     * Configures the password hashing mechanism using BCrypt.
     * BCrypt provides built-in salting and intentionally slow execution to protect against brute-force attacks.
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /**
     * Exposes the AuthenticationManager bean required for authentication workflows.
     */
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    /**
     * Defines the custom UserDetailsService bean to retrieve user profiles securely 
     * from the PostgreSQL database via UserRepository instead of in-memory lists.
     */
    @Bean
    public UserDetailsService userDetailsService(UserRepository userRepository) {
        return username -> userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found with username: " + username));
    }

    /**
     * Configures the main HTTP security filter chain, rules, stateless session policy, 
     * and filter ordering.
     */
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // Disabled as CSRF protection is unneeded for stateless JWT-based token architectures
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)) // Ensures Spring Security never creates or relies on HTTP sessions
            .authorizeHttpRequests(auth -> auth
                // 1. Explicit permitAll rules for public entry points, WebSockets, and M2M telemetry streams
                // ARCHITECTURAL NOTE (Telemetry Ingestion Bypass):
                // Python monitoring agents push high-frequency telemetry without human JWT sessions. 
                // Security is offloaded to lightweight token validation layers to eliminate JWT overhead on M2M streams.
                .requestMatchers(
                    "/api/login", 
                    "/api/auth/login", 
                    "/api/auth/verify-2fa", // Added support for the true 2FA verification endpoint
                    "/ws/**", 
                    "/api/telemetry/**", 
                    "/api/metrics/receiver", 
                    "/api/metrics/receiver/**", 
                    "/api/metrics/**", 
                    "/api/alerts/**" 
                ).permitAll()
                
                // 2. Restrict administrative user management endpoints strictly to users with the ADMIN role
                .requestMatchers("/api/users/**").hasRole("ADMIN")
                
                // 3. Fallback rule: Enforce JWT authentication for any other unmapped request
                .anyRequest().authenticated()
            )
            // 4. Register the custom JWT filter prior to the standard UsernamePasswordAuthenticationFilter in the chain
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    /**
     * Configures global CORS policies to permit integration with frontend clients and proxies (e.g., Nginx).
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList("*")); // Configured flexibly for local environments; restrict in production environments
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(false);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}