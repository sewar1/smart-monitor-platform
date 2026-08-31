package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.config.JwtService;
import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.security.LoginBruteForceProtector;
import com.sewarl.smartmonitor.service.UserService;
import com.sewarl.smartmonitor.service.TwoFactorAuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

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

    // Temporary in-memory cache to handle pending 2FA code verifications securely
    private final Map<String, String> pending2faCache = new ConcurrentHashMap<>();
 
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
     * 1. Validates input existence (both username and password).
     * 2. Checks against brute-force lockout status.
     * 3. Verifies credentials against the hashed database records.
     * 4. Triggers true 2FA workflow: dispatches OTP and returns PENDING_2FA state instead of raw JWT.
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest != null ? loginRequest.get("username") : null;
        String password = loginRequest != null ? loginRequest.get("password") : null;

        if (username == null || username.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Username is required"));
        }
        
        // Fix: Validate password presence to avoid unexpected exception in passwordEncoder.matches(null, hash)
        if (password == null || password.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Password is required"));
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

            // 4. True 2FA Workflow: Do not issue JWT immediately; enforce 2FA verification step
            if (adminEmail != null && !adminEmail.trim().isEmpty()) {
                String otpToken = twoFactorAuthService.generateVerificationToken();
                twoFactorAuthService.sendVerificationEmail(adminEmail, otpToken);
                
                // Store code temporarily for validation in the verify-2fa endpoint
                pending2faCache.put(username, otpToken);
                log.info("2FA token generated and dispatched for user: {}", username);

                // Return a structured pending response requiring second-factor validation
                return ResponseEntity.status(HttpStatus.ACCEPTED).body(Map.of(
                    "status", "PENDING_2FA",
                    "message", "Credentials verified. Please provide the 2FA verification code.",
                    "username", username
                ));
            }

            // Fallback if 2FA is unconfigured: Generate JWT Token so the frontend can access the dashboard
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
     * Endpoint to complete the true 2FA verification phase.
     * POST /api/auth/verify-2fa
     */
    @PostMapping("/verify-2fa")
    public ResponseEntity<?> verify2fa(@RequestBody Map<String, String> request) {
        String username = request != null ? request.get("username") : null;
        String code = request != null ? request.get("code") : null;

        if (username == null || code == null) {
            return ResponseEntity.badRequest().body(Map.of("error", "Username and code are required"));
        }

        String expectedCode = pending2faCache.get(username);
        if (expectedCode == null || !expectedCode.equals(code)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid or expired 2FA code"));
        }

        // Clean up pending cache
        pending2faCache.remove(username);

        Optional<User> userOpt = userService.findByUsername(username);
        if (userOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", "User not found"));
        }

        User authenticatedUser = userOpt.get();
        String jwtToken = jwtService.generateToken(authenticatedUser);

        log.info("2FA successfully completed for user: {}. JWT issued.", username);
        return ResponseEntity.ok(Map.of(
            "message", "2FA verification successful",
            "role", authenticatedUser.getRole(),
            "token", jwtToken
        ));
    }

    /**
     * Endpoint to check user registration profiles safely without exposing password hashes.
     * GET /api/auth/user/{username}
     * 
     * Useful for administrative lookups or initial identity verification during account setup.
     */
    @GetMapping("/user/{username}")
    public ResponseEntity<?> getUserProfile(@PathVariable String username) {
        Optional<User> userOpt = userService.findByUsername(username);
        if (userOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        
        User user = userOpt.get();
        // Return a sanitized map to prevent sensitive password hash exposure
        Map<String, Object> sanitizedProfile = Map.of(
            "id", user.getId(),
            "username", user.getUsername(),
            "email", user.getEmail() != null ? user.getEmail() : "",
            "role", user.getRole()
        );

        return ResponseEntity.ok(sanitizedProfile);
    }

    /**
     * Endpoint to provision a new user administrator account.
     * Protected via PreAuthorize to ensure only users with ADMIN role can register new accounts.
     * POST /api/auth/register
     */
    @PostMapping("/register")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> registerUser(@RequestBody User user) {
        if (user.getUsername() == null || user.getPassword() == null) {
            return ResponseEntity.badRequest().body(Map.of("error", "Username and password are required"));
        }
        User saved = userService.saveUser(user);
        
        Map<String, Object> sanitizedResponse = Map.of(
            "message", "User registered successfully",
            "username", saved.getUsername(),
            "role", saved.getRole()
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(sanitizedResponse);
    }
}