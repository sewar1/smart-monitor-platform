package com.sewarl.smartmonitor.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;

    // to inject the JWT filter into the security configuration
    public SecurityConfig(JwtAuthenticationFilter jwtAuthFilter) {
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

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // to stop CSRF attacks, since we are using JWTs for stateless authentication
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)) // to make the application stateless, as we are using JWTs
            .authorizeHttpRequests(auth -> auth
                // 1. to allow unauthenticated access to login, WebSocket and telemetry ingestion endpoints
                // ARCHITECTURAL NOTE (Telemetry Ingestion Bypass): 
                // We explicitly permit '/api/metrics/**' here to allow distributed system monitoring agents (Python) 
                // to push telemetry data without human JWT sessions. Security is not compromised; rather, it is 
                // offloaded to a lightweight, high-performance X-Agent-Token validation pattern handled inside 
                // the ingestion layer to prevent JWT overhead on high-frequency machine-to-machine (M2M) streams.
                .requestMatchers("/api/auth/login", "/ws/**", "/api/telemetry/**").permitAll()
                
                // 2. to restrict user management endpoints to ADMIN role only
                .requestMatchers("/api/users/**").hasRole("ADMIN")
                
                // 3. to require authentication for all other endpoints
                .anyRequest().authenticated()
            )
            // 4. to add the JWT filter before the default UsernamePasswordAuthenticationFilter
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
