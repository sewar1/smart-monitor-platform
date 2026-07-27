package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.config.JwtService;
import com.sewarl.smartmonitor.security.LoginBruteForceProtector;
import com.sewarl.smartmonitor.service.TwoFactorAuthService;
import com.sewarl.smartmonitor.service.UserService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

class AuthControllerTest {

    @Mock
    private UserService userService;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private LoginBruteForceProtector bruteForceProtector;

    @Mock
    private TwoFactorAuthService twoFactorAuthService;

    @Mock
    private JwtService jwtService;

    @InjectMocks
    private AuthController authController;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testLoginRequiresUsername() {
        Map<String, String> request = Map.of("password", "secret");
        ResponseEntity<?> response = authController.login(request);

        assertEquals(400, response.getStatusCode().value());
    }

    @Test
    void testLoginFailsWhenAccountIsLocked() {
        Map<String, String> request = Map.of("username", "lockeduser", "password", "secret");
        
        // Mock the bruteForceProtector to simulate a locked account
        when(bruteForceProtector.getRemainingLockoutTime("lockeduser")).thenReturn(300L);

        ResponseEntity<?> response = authController.login(request);

        assertEquals(423, response.getStatusCode().value(), "Locked status HTTP 423 expected");
    }
}