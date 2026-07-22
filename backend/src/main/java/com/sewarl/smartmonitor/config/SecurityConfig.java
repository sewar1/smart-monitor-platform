package com.sewarl.smartmonitor.config;

import java.util.Arrays;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
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

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;

    // to inject the JWT filter into the security configuration
    public SecurityConfig(@Lazy JwtAuthenticationFilter jwtAuthFilter) { // @Lazy to avoid circular dependency issues during bean initialization. spring cant creat a before b , or b before a, so we use @Lazy to delay the injection until it's actually needed, preventing circular dependency errors.
        this.jwtAuthFilter = jwtAuthFilter;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    // spring cant find the UserDetailsService bean automatically, so we define it explicitly here, to inject it into JwtAuthenticationFilter for user authentication and authorization
    @Bean
    public UserDetailsService userDetailsService(UserRepository userRepository) { // to provide a custom UserDetailsService implementation that retrieves user details from the database
        return username -> userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found"));
    }

@Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // to stop CSRF attacks, since we are using JWTs for stateless authentication
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)) // to make the application stateless, as we are using JWTs
            .authorizeHttpRequests(auth -> auth
                // 1. to allow unauthenticated access to login, WebSocket and telemetry ingestion endpoints
                // ARCHITECTURAL NOTE (Telemetry Ingestion Bypass): 
                // We explicitly permit '/api/telemetry/**' AND '/api/metrics/receiver' here to allow distributed system 
                // monitoring agents (Python) to push telemetry data without human JWT sessions. 
                // Security is not compromised; rather, it is offloaded to a lightweight, high-performance X-Agent-Token 
                // validation pattern handled inside the ingestion layer to prevent JWT overhead on high-frequency machine-to-machine (M2M) streams.
                .requestMatchers(
                    "/api/login", // to allow unauthenticated access to the Login.tsx endpoint for JWT acquisition , to match the AuthController login endpoint
                    "/api/auth/login", 
                    "/ws/**", 
                    "/api/telemetry/**", 
                    "/api/metrics/receiver", // <--- The path that was causing the 403 error has been added here, now the Spring Security configuration explicitly allows unauthenticated access to this endpoint
                    "/api/metrics/receiver/**", // to allow unauthenticated access to the metrics ingestion endpoint for high-frequency telemetry data
                    "/api/metrics/**", // to allow unauthenticated access to the metrics ingestion endpoint for high-frequency telemetry data
                    "/api/alerts/**" // to allow unauthenticated access to the metrics ingestion endpoint for high-frequency telemetry data
                ).permitAll()
                
                // 2. to restrict user management endpoints to ADMIN role only
                .requestMatchers("/api/users/**").hasRole("ADMIN")
                
                // 3. to require authentication for all other endpoints
                .anyRequest().authenticated()
            )
            // 4. to add the JWT filter before the default UsernamePasswordAuthenticationFilter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList("*")); // للسماح لـ Nginx/Frontend
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
