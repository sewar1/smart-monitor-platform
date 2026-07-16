package com.sewarl.smartmonitor.repository;

import com.sewarl.smartmonitor.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

/**
 * JPA Data Access Layer for User Security operations.
 * Auto-registered by Spring Data JPA (No @Repository annotation needed).
 */
public interface UserRepository extends JpaRepository<User, Integer> { // Using Integer to match the PostgreSQL 'SERIAL' data type defined in init.sql
    
    Optional<User> findByUsername(String username);
    boolean existsByUsername(String username); // Convenience method to check for username uniqueness before registration
}