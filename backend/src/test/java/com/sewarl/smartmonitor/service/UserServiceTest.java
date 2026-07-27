package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testSaveUserEncodesPasswordIfNotAlreadyEncoded() {
        User user = new User();
        user.setUsername("testuser");
        user.setPassword("plainPassword123");

        when(passwordEncoder.encode("plainPassword123")).thenReturn("$2a$10$encodedPasswordHash");
        when(userRepository.save(any(User.class))).thenReturn(user);

        User saved = userService.saveUser(user);

        assertNotNull(saved);
        assertEquals("$2a$10$encodedPasswordHash", saved.getPassword());
        verify(passwordEncoder, times(1)).encode("plainPassword123");
        verify(userRepository, times(1)).save(user);
    }

    @Test
    void testSaveUserThrowsExceptionWhenNull() {
        assertThrows(IllegalArgumentException.class, () -> {
            userService.saveUser(null);
        });
    }

    @Test
    void testFindByUsername() {
        User user = new User();
        user.setUsername("admin");
        when(userRepository.findByUsername("admin")).thenReturn(Optional.of(user));

        Optional<User> result = userService.findByUsername("admin");
        assertTrue(result.isPresent());
        assertEquals("admin", result.get().getUsername());
    }
}