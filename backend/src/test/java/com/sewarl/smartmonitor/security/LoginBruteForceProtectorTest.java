package com.sewarl.smartmonitor.security;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class LoginBruteForceProtectorTest {

    private LoginBruteForceProtector bruteForceProtector;

    @BeforeEach
    void setUp() {
        bruteForceProtector = new LoginBruteForceProtector();
    }

    @Test
    void testInitialStateIsNotLocked() {
        String username = "testuser";
        long remainingTime = bruteForceProtector.getRemainingLockoutTime(username);
        assertEquals(0, remainingTime, "New user should not have any lockout time");
    }

    @Test
    void testLockoutAfterMaxAttempts() {
        String username = "attacker";

        // Simulate 5 failed login attempts
        for (int i = 0; i < 5; i++) {
            bruteForceProtector.registerFailure(username);
        }

        // Verify that the account is locked and the remaining time is greater than zero
        long remainingTime = bruteForceProtector.getRemainingLockoutTime(username);
        assertTrue(remainingTime > 0, "Account should be locked after 5 failed attempts");
    }

    @Test
    void testResetAttemptsClearsLockout() {
        String username = "user123";

        // Simulate failed login attempts up to the lockout threshold
        for (int i = 0; i < 5; i++) {
            bruteForceProtector.registerFailure(username);
        }

        // Verify that the account is locked
        assertTrue(bruteForceProtector.getRemainingLockoutTime(username) > 0);

        // Reset the attempts (as would happen upon successful login)
        bruteForceProtector.resetAttempts(username);

        // Verify that the lockout is cleared and the remaining time is back to zero
        assertEquals(0, bruteForceProtector.getRemainingLockoutTime(username), "Lockout should be cleared after reset");
    }
}
