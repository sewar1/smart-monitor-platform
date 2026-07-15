package com.sewarl.smartmonitor.config;

import com.sewarl.smartmonitor.entity.User;
import com.sewarl.smartmonitor.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class DatabaseSeeder implements CommandLineRunner {

    private final UserService userService;

    @Override
    public void run(String... args) throws Exception {
        log.info("Checking database for default administrative profile...");
        
        // Seed a default admin user if none exists
        if (userService.findByUsername("admin").isEmpty()) {
            log.info("No default administrator found. Initializing secure admin seeding...");
            
            User admin = new User();
            admin.setUsername("admin");
            admin.setPassword("secure_admin_password_2026"); // سيقوم UserService بتشفيرها تلقائياً بـ BCrypt
            admin.setRole("ADMIN");
            
            userService.saveUser(admin);
            log.info("🎉 Default system administrator profile seeded successfully!");
        } else {
            log.info("Administrative profile already exists. Skipping database seeding.");
        }
    }
}
