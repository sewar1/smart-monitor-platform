package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.config.JwtService;
import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.security.LoginBruteForceProtector;
import com.sewarl.smartmonitor.service.UserService;
import com.sewarl.smartmonitor.service.TwoFactorAuthService;
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
 * 
 * This controller serves as the primary gateway for user identity verification.
 * It integrates with LoginBruteForceProtector to mitigate automated credential stuffing attacks.
 */
@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final UserService userService;
    private final PasswordEncoder passwordEncoder;
    private final LoginBruteForceProtector bruteForceProtector;
    private final TwoFactorAuthService twoFactorAuthService;
    private final JwtService jwtService;
    private static final Logger log = LoggerFactory.getLogger(AuthController.class);
 
    /**
     * Explicit structural constructor injection. 
     * Eliminates Lombok annotation processing dependencies to guarantee thread-safe initialization 
     * and facilitate easier unit testing via mock injection.
     */
    public AuthController(UserService userService, 
                          PasswordEncoder passwordEncoder, 
                          LoginBruteForceProtector bruteForceProtector,
                          TwoFactorAuthService twoFactorAuthService,
                          JwtService jwtService) {
        this.userService = userService;
        this.passwordEncoder = passwordEncoder;
        this.bruteForceProtector = bruteForceProtector;
        this.twoFactorAuthService = twoFactorAuthService;
        this.jwtService = jwtService;
    }

    /**
     * Authenticates an identity sequence while routing through the dynamic brute-force mitigation gateway.
     * POST /api/auth/login
     * 
     * This method handles the core authentication logic:
     * 1. Validates input existence.
     * 2. Checks against brute-force lockout status.
     * 3. Verifies credentials against the hashed database records.
     * 4. Triggers 2FA workflow if authentication succeeds.
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");

        if (username == null || username.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Username is required"));
        }

        // 1. Pre-Auth Boundary Check: Assess if identity footprint is currently restricted by the security gate
        long remainingLockoutSeconds = bruteForceProtector.getRemainingLockoutTime(username);
        if (remainingLockoutSeconds > 0) {
            long minutesLeft = (remainingLockoutSeconds / 60) + 1;
            return ResponseEntity.status(HttpStatus.LOCKED) // HTTP Status 423: Locked
                    .body(Map.of("error", "Account temporarily locked. Too many failed attempts. Please retry after " + minutesLeft + " minutes."));
        }

        // 2. Locate the secure profile inside PostgreSQL
        Optional<User> userOpt = userService.findByUsername(username);

        // 3. Cryptographic Signature Verification using BCrypt
        if (userOpt.isPresent() && passwordEncoder.matches(password, userOpt.get().getPassword())) {
            // Success State -> Immediately purge failure thresholds from the in-memory cache
            bruteForceProtector.resetAttempts(username);

            User authenticatedUser = userOpt.get();
            String adminEmail = authenticatedUser.getEmail(); 

            // Initialize 2FA process if the account is configured for enhanced security
            if (adminEmail != null && !adminEmail.trim().isEmpty()) {
                String otpToken = twoFactorAuthService.generateVerificationToken();
                twoFactorAuthService.sendVerificationEmail(adminEmail, otpToken);
                log.info("2FA token generated and dispatched for user: {}", username);
            }

            // Generate JWT Token so the frontend can store it and access the dashboard
            String jwtToken = jwtService.generateToken(authenticatedUser);
            
            return ResponseEntity.ok(Map.of(
                "message", "Login successful", 
                "role", authenticatedUser.getRole(),
                "token", jwtToken // JWT token for frontend session management
            ));
        } else {
            // Reactive Security Path -> Register failure trace vector to throttle future requests for this identity
            bruteForceProtector.registerFailure(username);
            
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED) // HTTP Status 401: Unauthorized
                    .body(Map.of("error", "Invalid username or password"));
        }
    }

    /**
     * Endpoint to check user registration profiles.
     * GET /api/auth/user/{username}
     * 
     * Useful for administrative lookups or initial identity verification during account setup.
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