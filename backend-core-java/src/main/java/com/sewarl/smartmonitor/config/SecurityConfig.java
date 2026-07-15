package com.sewarl.smartmonitor.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration // Spring configuration class for security settings
@EnableWebSecurity // Enables Spring Security's web security support and provides the Spring MVC integration
public class SecurityConfig {

    // Bean for password encoding using BCrypt hashing algorithm
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // API security filter chain configuration
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // Disable CSRF protection for stateless REST APIs
            .authorizeHttpRequests(auth -> auth.anyRequest().permitAll()); // Allow all requests without authentication for now (can be tightened later)
        return http.build();
    }
}
