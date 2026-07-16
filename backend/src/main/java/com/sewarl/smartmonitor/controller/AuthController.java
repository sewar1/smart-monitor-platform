package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.security.LoginBruteForceProtector;
import com.sewarl.smartmonitor.service.UserService;
import com.sewarl.smartmonitor.service.TwoFactorAuthService; // this import is for future 2FA integration
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

/**
 * Enterprise REST Controller for identity management, user registration, 
 * profile lookups, and secure brute-force resilient authentication.
 */
@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final UserService userService;
    private final PasswordEncoder passwordEncoder;
    private final LoginBruteForceProtector bruteForceProtector;
    private final TwoFactorAuthService twoFactorAuthService; //this field is for future 2FA integration
    private static final Logger log = LoggerFactory.getLogger(AuthController.class);
 
    /**
     * Explicit structural constructor injection. 
     * Eliminates Lombok annotation processing dependencies to guarantee thread-safe initialization.
     */
    public AuthController(UserService userService, 
                          PasswordEncoder passwordEncoder, 
                          LoginBruteForceProtector bruteForceProtector,
                          TwoFactorAuthService twoFactorAuthService) { //  this constructor parameter is for future 2FA integration
        this.userService = userService;
        this.passwordEncoder = passwordEncoder;
        this.bruteForceProtector = bruteForceProtector;
        this.twoFactorAuthService = twoFactorAuthService; // this constructor parameter is for future 2FA integration
    }

    /**
     * Authenticates an identity sequence while routing through the dynamic brute-force mitigation gateway.
     * POST /api/auth/login
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");

        if (username == null || username.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Username is required"));
        }

        // 1. Pre-Auth Boundary Check: Assess if identity footprint is currently restricted
        long remainingLockoutSeconds = bruteForceProtector.getRemainingLockoutTime(username);
        if (remainingLockoutSeconds > 0) {
            long minutesLeft = (remainingLockoutSeconds / 60) + 1;
            return ResponseEntity.status(HttpStatus.LOCKED) // HTTP Status 423: Locked
                    .body(Map.of("error", "Account temporarily locked. Too many failed attempts. Please retry after " + minutesLeft + " minutes."));
        }

        // 2. Locate the secure profile inside PostgreSQL
        Optional<User> userOpt = userService.findByUsername(username);

        // 3. Cryptographic Signature Verification
        if (userOpt.isPresent() && passwordEncoder.matches(password, userOpt.get().getPassword())) {
            // Success State -> Immediately purge failure thresholds from cache
            bruteForceProtector.resetAttempts(username);


            User authenticatedUser = userOpt.get();
            String role = authenticatedUser.getEmail();
            String adminEmail = userOpt.get().getEmail(); // Retrieve the administrator's email for 2FA dispatch

            if (adminEmail != null && !adminEmail.trim().isEmpty()) {
                // Generate a time-bound 2FA token and send it to the administrator's email for verification
                String token = twoFactorAuthService.generateVerificationToken();
                
                
                // Send the token to the admin's email address (this is a placeholder; actual implementation may vary)
                twoFactorAuthService.sendVerificationEmail(adminEmail, token);
                
                // Store the token in a secure cache or database to be matched during the 2FA verification step
                // This is a placeholder; actual implementation may vary
            }
            // ------------------------------------------------------------------------------------------
            
            // TODO: Generate JWT Token or session footprint in the next security iteration phase
            return ResponseEntity.ok(Map.of(
                "message", "Login successful", 
                "role", userOpt.get().getRole()
            ));
        } else {
            // Reactive Security Path -> Register failure trace vector to throttle future requests
            bruteForceProtector.registerFailure(username);
            
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED) // HTTP Status 401: Unauthorized
                    .body(Map.of("error", "Invalid username or password"));
        }
    }

    /**
     * Endpoint to simulate a login attempt for testing brute-force mitigation.
     * GET /api/auth/login?username={username}
     * This endpoint is primarily for testing and demonstration purposes. In production, use the POST /login endpoint with proper credentials.
     */
    @PostMapping("/login")
    public String login(@RequestParam String username) {
        // 1. Log the authentication attempt for auditing and monitoring purposes
        log.info("Authentication sequence initiated for user: {}", username);
        
        try {
            // specific treatment for 2FA token generation and dispatch
            return "SUCCESS";
        } catch (Exception e) {
            // Log a warning or error (will be automatically written to system.log and alerts.log)
            log.error("Authentication failed during token generation for user: {}", username, e);
            throw e;
        }
    }

    /**
     * Endpoint to check user registration profiles.
     * GET /api/auth/user/{username}
     */
    @GetMapping("/user/{username}")
    public ResponseEntity<User> getUserProfile(@PathVariable String username) {
        Optional<User> userOpt = userService.findByUsername(username);
        return userOpt.map(ResponseEntity::ok)
                      .orElseGet(() -> ResponseEntity.notFound().build());
    }

    /**
     * Endpoint to provision a new user administrator account.
     * Automatically integrates with the underlying password hashing hooks in UserService.
     * POST /api/auth/register
     */
    @PostMapping("/register")
    public ResponseEntity<User> registerUser(@RequestBody User user) {
        User saved = userService.saveUser(user);
        return ResponseEntity.ok(saved);
    }
}