package main.java.com.sewarl.smartmonitor.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.mail.javamail.JavaMailSender;

import static org.junit.jupiter.api.Assertions.*;

class TwoFactorAuthServiceTest {

    @Mock
    private JavaMailSender mailSender;

    private TwoFactorAuthService twoFactorAuthService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        twoFactorAuthService = new TwoFactorAuthService(mailSender);
    }

    @Test
    void testGenerateVerificationTokenReturnsSixDigits() {
        String token = twoFactorAuthService.generateVerificationToken();

        assertNotNull(token);
        assertEquals(6, token.length(), "Token must be exactly 6 digits long");
        assertTrue(token.matches("\\d{6}"), "Token must contain only numeric characters");
    }
}