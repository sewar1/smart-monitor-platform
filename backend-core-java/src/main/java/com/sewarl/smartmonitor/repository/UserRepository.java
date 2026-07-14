package com.sewarl.smartmonitor.repository;

import com.sewarl.smartmonitor.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

/**
 * JPA Data Access Layer for User Security operations.
 * Auto-registered by Spring Data JPA (No @Repository annotation needed).
 */
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByUsername(String username);
}