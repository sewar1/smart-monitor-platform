package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

/**
 * Initial REST Controller for managing user identity and dashboard login lookups.
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {

    private final UserService userService;

    /**
     * Endpoint to check user registration profiles.
     * GET /api/auth/user/{username}
     */
    @SuppressWarnings("null")
    @GetMapping("/user/{username}")
    public ResponseEntity<User> getUserProfile(@PathVariable String username) {
        Optional<User> userOpt = userService.findByUsername(username);
        return userOpt.map(ResponseEntity::ok)
                      .orElseGet(() -> ResponseEntity.notFound().build());
    }

    /**
     * Endpoint to provision a new user administrator account.
     * POST /api/auth/register
     */
    @PostMapping("/register")
    public ResponseEntity<User> registerUser(@RequestBody User user) {
        User saved = userService.saveUser(user);
        return ResponseEntity.ok(saved);
    }
}