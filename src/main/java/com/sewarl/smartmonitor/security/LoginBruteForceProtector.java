package com.sewarl.smartmonitor.security;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Smart Monitor Platform - Brute Force Mitigation Gateway.
 * Thread-safe in-memory security core designed to block brute-force vectors in high-concurrency environments.
 */
@Component
public class LoginBruteForceProtector {

    private static final Logger log = LoggerFactory.getLogger(LoginBruteForceProtector.class);

    private final int maxAttempts = 5;
    private final long lockoutDurationSeconds = 900; // 15 minutes matching python security_gate config

    // Thread-safe in-memory maps to track identity execution footprints safely across multiple concurrent requests
    private final Map<String, Integer> failedAttempts = new ConcurrentHashMap<>();
    private final Map<String, Instant> lockoutTimers = new ConcurrentHashMap<>();

    /**
     * Evaluates if a specific identity sequence is currently blocked under security lockout.
     * @return remaining lockout time in seconds if locked, 0 otherwise.
     */
    public long getRemainingLockoutTime(String username) {
        if (username == null) return 0;
        
        String cleanUsername = username.trim();
        Instant lockoutExpiry = lockoutTimers.get(cleanUsername);

        if (lockoutExpiry != null) {
            long remainingTime = lockoutExpiry.getEpochSecond() - Instant.now().getEpochSecond();
            if (remainingTime > 0) {
                return remainingTime;
            } else {
                // The lockdown period has automatically expired; reset the tracking ledger
                resetAttempts(cleanUsername);
            }
        }
        return 0;
    }

    /**
     * Increments the failure token counter and triggers dynamic identity lockout if boundaries are breached.
     */
    public void registerFailure(String username) {
        if (username == null) return;
        
        String cleanUsername = username.trim();
        int currentCount = failedAttempts.getOrDefault(cleanUsername, 0) + 1;
        failedAttempts.put(cleanUsername, currentCount);

        if (currentCount >= maxAttempts) {
            Instant expiryTime = Instant.now().plusSeconds(lockoutDurationSeconds);
            lockoutTimers.put(cleanUsername, expiryTime);
            log.error("[SECURITY ALERT] Identity [{}] has been LOCKED OUT for 15 minutes due to excessive authentication failures.", cleanUsername);
        }
    }

    /**
     * Clears all anomaly tracking thresholds for an authenticated user.
     */
    public void resetAttempts(String username) {
        if (username == null) return;
        
        String cleanUsername = username.trim();
        failedAttempts.remove(cleanUsername);
        lockoutTimers.remove(cleanUsername);
    }
}
