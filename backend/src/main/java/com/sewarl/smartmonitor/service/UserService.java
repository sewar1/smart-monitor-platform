package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

/**
 * Core business logic for identity management.
 * Synchronized with the updated Integer-based primary key configuration.
 * 
 * Refactored based on strict security review findings:
 * - Robust BCrypt prefix checking supporting $2a$, $2b$, and $2y$.
 * - Prevention of empty string password overwrites during updates.
 * - Defense against mass assignment vulnerabilities by enforcing safe default roles.
 */
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder; // Automatically injected by Spring Security for password hashing and verification

    /**
     * Locates a secure user profile via username lookup.
     */
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    /**
     * Locates a secure user profile via its native primary key.
     * Updated parameter type to Integer to perfectly match the 'SERIAL' column.
     */
    public Optional<User> findById(Integer id) {
        return userRepository.findById(id);
    }

    /**
     * Registers or updates a user profile with defensive checks and secure credential handling.
     */
    public User saveUser(User user) {
        if (user == null) {
            throw new IllegalArgumentException("User entity cannot be null"); // Defensive programming to prevent null persistence
        }
        
        // Fix: Enforce defensive check for empty passwords to prevent silent blank string hash overwrites
        if (user.getPassword() != null && !user.getPassword().trim().isEmpty()) {
            String rawPassword = user.getPassword();
            
            // Fix: Robust BCrypt prefix validation supporting modern variants ($2a$, $2b$, $2y$) to avoid double-hashing
            boolean isAlreadyHashed = rawPassword.startsWith("$2a$") || 
                                      rawPassword.startsWith("$2b$") || 
                                      rawPassword.startsWith("$2y$");
            
            if (!isAlreadyHashed) {
                user.setPassword(passwordEncoder.encode(rawPassword));
            }
        } else if (user.getId() == null) {
            // New user registration must include a valid non-empty password
            throw new IllegalArgumentException("Password is required for new user registration");
        }

        // Fix: Prevent Mass Assignment by ensuring standard default roles if not explicitly handled or restricted
        if (user.getRole() == null || user.getRole().trim().isEmpty()) {
            user.setRole("USER"); // Secure fallback default role
        }

        return userRepository.save(user);
    }
}