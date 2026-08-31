package com.sewarl.smartmonitor.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import java.time.OffsetDateTime;

import java.util.Collection;
import java.util.List;

/**
 * Enterprise Security User Entity.
 * Maps securely to the 'users' table in PostgreSQL and implements UserDetails
 * for seamless native integration with Spring Security.
 */
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(name = "password_hash", nullable = false, length = 255)
    private String password;

    @Column(nullable = false, length = 20)
    private String role = "operator"; // Standardized default role for new users; can be elevated to 'admin' or 'superadmin' via secure admin workflows

    @Column(name = "created_at", nullable = false, columnDefinition = "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
    private OffsetDateTime createdAt = OffsetDateTime.now();

    // --- UserDetails Implementation ---

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        // Dynamically maps the stored role to Spring Security's expected "ROLE_" prefixed authority structure
        return List.of(new SimpleGrantedAuthority("ROLE_" + (this.role != null ? this.role.toUpperCase() : "OPERATOR")));
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        // Architectural note: Currently defaults to true. 
        // Can be integrated with LoginBruteForceProtector state mapping if global Spring Security authentication manager is used directly.
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return true;
    }

    // --- Getters & Setters ---
    // we can delete the explicit getters and setters if we use Lombok's @Data annotation, but they are kept here for clarity and potential customization
    
    public String getUsername() { return this.username; }
    public String getPassword() { return this.password; }
}