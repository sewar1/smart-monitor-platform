package com.sewarl.smartmonitor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.scheduling.annotation.EnableScheduling; // spring scheduling for periodic tasks

@SpringBootApplication(exclude = { SecurityAutoConfiguration.class })
@EnableScheduling // to enable scheduled tasks for periodic metric purging and alerting
public class SmartmonitorApplication {

	public static void main(String[] args) {
		SpringApplication.run(SmartmonitorApplication.class, args);
	}

}
