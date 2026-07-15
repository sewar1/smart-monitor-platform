package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder; // Ticket 3 : this import is for future password hashing integration
import org.springframework.stereotype.Service;

import java.util.Optional;

/**
 * Core business logic for identity management.
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
     * Registers or updates a user profile.
     */
    public User saveUser(User user) {
        // Password hashing hook will integrate directly here in later security phases
        if (user == null) {
            throw new IllegalArgumentException("User entity cannot be null"); // Defensive programming to prevent null persistence
        }
        // If the password is not already hashed, hash it before saving
        if (user.getPassword() != null && !user.getPassword().startsWith("$2a$")) { 
            user.setPassword(passwordEncoder.encode(user.getPassword()));
        }


        return userRepository.save(user);
    }
}