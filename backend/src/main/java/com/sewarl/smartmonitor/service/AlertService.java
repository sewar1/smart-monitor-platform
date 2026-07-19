package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.MetricAlert;
import com.sewarl.smartmonitor.repository.AlertRepository;
// Import your Metric entity (Adjust path if package differs in your project)
import com.sewarl.smartmonitor.entity.Metric;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Core business logic for managing node anomaly logs, persisting incidents,
 * and dispatching real-time notifications via SMTP (Email) and Telegram Bot APIs.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AlertService {

    private final AlertRepository alertRepository;
    private final JavaMailSender mailSender; // Spring Boot's built-in SMTP engine
    private final RestTemplate restTemplate = new RestTemplate(); // Pure Java HTTP Client for Telegram API

    // --- Injecting configuration parameters from application.yaml ---

    @Value("${spring.mail.username}")
    private String mailFrom;

    @Value("${app.alerts.email-to}")
    private String mailTo;

    @Value("${app.alerts.telegram.bot-token}")
    private String telegramBotToken;

    @Value("${app.alerts.telegram.chat-id}")
    private String telegramChatId;

    // --- Injecting infrastructure thresholds with safe fallbacks (Ticket 9 Nomenclature) ---

    @Value("${app.alerts.cpu-threshold:85.0}")
    private BigDecimal cpuThreshold;

    @Value("${app.alerts.ram-threshold:85.0}")
    private BigDecimal ramThreshold;

    @Value("${app.alerts.disk-threshold:90.0}")
    private BigDecimal diskThreshold;


    /**
     * Evaluates incoming real-time telemetry from an edge node against configured thresholds.
     * Ported and migrated from python's alerts.py to provide centralized Backend alerting.
     */
    public void evaluateInfrastructureNode(Metric metric) {
        String nodeId = metric.getNodeId();
        String location = metric.getLocation() != null ? metric.getLocation() : "Unknown";

        // 1. Evaluate CPU Usage
        if (metric.getCpuUsage().compareTo(cpuThreshold) > 0) {
            String message = String.format("⚠️ [%s] (%s) - HIGH CPU USAGE: %.1f%% (Threshold: %.1f%%)",
                    nodeId, location, metric.getCpuUsage(), cpuThreshold);
            sendCriticalAlert(nodeId, "HIGH_CPU_USAGE", message);
        }

        // 2. Evaluate RAM Usage
        if (metric.getRamUsage().compareTo(ramThreshold) > 0) {
            String message = String.format("⚠️ [%s] (%s) - HIGH RAM USAGE: %.1f%% (Threshold: %.1f%%)",
                    nodeId, location, metric.getRamUsage(), ramThreshold);
            sendCriticalAlert(nodeId, "HIGH_RAM_USAGE", message);
        }

        // 3. Evaluate Disk Usage
        if (metric.getDiskUsage().compareTo(diskThreshold) > 0) {
            String message = String.format("⚠️ [%s] (%s) - HIGH DISK USAGE: %.1f%% (Threshold: %.1f%%)",
                    nodeId, location, metric.getDiskUsage(), diskThreshold);
            sendCriticalAlert(nodeId, "HIGH_DISK_USAGE", message);
        }
    }



    /**
     * Records a critical event or warning dispatched by an edge node.
     */
    public MetricAlert recordAlert(MetricAlert alert) {
        if (alert.getTimestamp() == null) {
            alert.setTimestamp(OffsetDateTime.now());
        }
        log.warn("🚨 [ALERT INBOUND] Node {} generated: {}", alert.getNodeId(), alert.getMessage());
        return alertRepository.save(alert);
    }

    /**
     * Entry point used by MetricService or other components to flag critical state failures.
     * Persists the incident locally and dispatches external alerts via Email and Telegram asynchronously.
     */
    public void sendCriticalAlert(String nodeId, String alertType, String message) {
        log.info("Initiating critical alerting pipelines for node: {}", nodeId);

        // 1. Persist the alert in our local database
        MetricAlert alert = new MetricAlert();
        alert.setNodeId(nodeId);
        alert.setAlertType(alertType);
        alert.setMessage(message);
        alert.setTimestamp(OffsetDateTime.now());
        recordAlert(alert);

        // 2. Dispatch notifications to external channels
        sendEmailAlert(nodeId, alertType, message);
        sendTelegramAlert(nodeId, alertType, message);
    }

    /**
     * Pure Java SMTP implementation to dispatch warning logs to system administrators.
     */
    private void sendEmailAlert(String nodeId, String alertType, String message) {
        try {
            SimpleMailMessage mailMessage = new SimpleMailMessage();
            mailMessage.setFrom(mailFrom);
            mailMessage.setTo(mailTo);
            mailMessage.setSubject(String.format("⚠️ [SMART MONITOR] %s Alert on Node: %s", alertType, nodeId));
            mailMessage.setText(String.format(
                "Attention Administrator,\n\n" +
                "A critical alert has been captured on your cluster:\n" +
                "--------------------------------------------------\n" +
                "Node ID:    %s\n" +
                "Alert Type: %s\n" +
                "Timestamp:  %s\n" +
                "Details:    %s\n" +
                "--------------------------------------------------\n\n" +
                "Please inspect the web dashboard to mitigate further failures.",
                nodeId, alertType, OffsetDateTime.now(), message
            ));

            mailSender.send(mailMessage);
            log.info("Email alert successfully sent to: {}", mailTo);
        } catch (Exception e) {
            log.error("Failed to dispatch SMTP alert for node {}: {}", nodeId, e.getMessage());
        }
    }

    /**
     * Dispatches real-time structured Telegram messages using direct bot API calls.
     */
    private void sendTelegramAlert(String nodeId, String alertType, String message) {
        // Safe check: prevent execution if telegram configurations are left blank
        if (telegramBotToken == null || telegramBotToken.isEmpty() || "YOUR_BOT_TOKEN".equals(telegramBotToken)) {
            log.warn("Telegram alerting skipped: Bot Token is unconfigured.");
            return;
        }

        try {
            String url = String.format("https://api.telegram.org/bot%s/sendMessage", telegramBotToken);

            // Constructing Telegram message with Markdown styling
            String formattedMessage = String.format(
                "🚨 *CRITICAL ALERT DETECTED*\n\n" +
                "🖥 *Node:* `%s`\n" +
                "⚠️ *Type:* `%s`\n" +
                "📝 *Message:* %s\n" +
                "⏰ *Time:* `%s`",
                nodeId, alertType, message, OffsetDateTime.now().toString()
            );

            // Build request body payload
            Map<String, String> requestBody = new HashMap<>();
            requestBody.put("chat_id", telegramChatId);
            requestBody.put("text", formattedMessage);
            requestBody.put("parse_mode", "Markdown");

            restTemplate.postForEntity(url, requestBody, String.class);
            log.info("Telegram notification successfully dispatched to chat ID: {}", telegramChatId);
        } catch (Exception e) {
            log.error("Failed to dispatch Telegram API alert for node {}: {}", nodeId, e.getMessage());
        }
    }

    /**
     * Retrieves all alerts ordered by recent occurrence.
     */
    public List<MetricAlert> getAllAlerts() {
        return alertRepository.findAllByOrderByTimestampDesc();
    }

    /**
     * Retrieves incidents filtered by a single node identifier.
     */
    public List<MetricAlert> getAlertsByNode(String nodeId) {
        return alertRepository.findByNodeIdOrderByTimestampDesc(nodeId);
    }
}