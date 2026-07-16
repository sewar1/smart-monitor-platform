package com.sewarl.smartmonitor.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.OffsetDateTime;

/**
 * Enterprise Security User Entity.
 * Maps securely to the 'users' table in PostgreSQL.
 */
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    // Using Integer to match the PostgreSQL 'SERIAL' data type defined in init.sql
    private Integer id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false, unique = true, length = 100) // Email field added for future multi-factor authentication and notification purposes
    private String email;

    // Explicitly mapping to the 'password_hash' column defined in schema
    @Column(name = "password_hash", nullable = false, length = 255)
    private String password;

    // Matches 'operator' as defined in the default schema value
    @Column(nullable = false, length = 20)
    private String role = "operator";

    // Adding created_at tracking to align with the SQL schema structure
    @Column(name = "created_at", nullable = false, columnDefinition = "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
    private OffsetDateTime createdAt = OffsetDateTime.now();

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getUsername() {
        return this.username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return this.password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getRole() {
        return this.role;
    }

    public void setRole(String role) {
        this.role = role;
    }
}