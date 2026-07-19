package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder; // Ticket 3 : this import is for future password hashing integration
import org.springframework.stereotype.Service;



import java.util.Optional;

/**
 * Core business logic for identity management.
 * Synchronized with the updated Integer-based primary key configuration.
 */
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder; // automatically injected by Spring Security for password hashing and verification

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
     * Registers or updates a user profile.
     */
    public User saveUser(User user) {
        if (user == null) {
            throw new IllegalArgumentException("User entity cannot be null"); // Defensive programming to prevent null persistence
        }
        
        // Securely hash the password before sending the record to PostgreSQL if not already BCrypt encoded
        if (user.getPassword() != null && !user.getPassword().startsWith("$2a$")) { 
            user.setPassword(passwordEncoder.encode(user.getPassword()));
        }

        return userRepository.save(user);
    }
}