package com.sewarl.smartmonitor.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * SMART MONITOR PLATFORM - INFRASTRUCTURE HEALTH ANALYZER & ANTI-FREEZE GUARD
 * 
 * Multi-criteria system status analysis engine and process investigator.
 * Engineered with OS-level process lifecycle guards to prevent execution race conditions.
 * Includes an automated programmatic Out-Of-Memory (OOM) mitigation subsystem.
 */
@Service
public class SystemAnalyzerService {

    private static final Logger log = LoggerFactory.getLogger(SystemAnalyzerService.class);

    // Ticket 5: Whitelist of critical system processes that must NEVER be terminated by the mitigation subsystem
    private static final List<String> CRITICAL_PROCESS_WHITELIST = List.of(
        "systemd", "init", "sshd", "bash", "python", "python3", "nginx",
        "apache2", "mysqld", "postgres", "postgres_engine", "java", "javaw",
        "redis-server", "db", "dockerd", "containerd",
        "smart-monitor-dashboard", "smart_monitor_agent_docker",
        "gunicorn", "gunicorn: master", "gunicorn: worker"
    );

    private final double cpuWeight;
    private final double ramWeight;
    private final double diskWeight;

    /**
     * Default constructor allocating the standard balanced weights matrix.
     */
    public SystemAnalyzerService() {
        this(0.4, 0.4, 0.2);
    }

    /**
     * Parameterized constructor to dynamically allocate telemetry weights.
     * Weights must precisely sum up to 1.0 (100%).
     */
    public SystemAnalyzerService(double cpuWeight, double ramWeight, double diskWeight) {
        double totalWeight = cpuWeight + ramWeight + diskWeight;
        if (Math.abs(totalWeight - 1.0) > 1e-9) {
            throw new IllegalArgumentException("Telemetry weights allocation matrix must precisely sum up to 1.0");
        }
        this.cpuWeight = cpuWeight;
        this.ramWeight = ramWeight;
        this.diskWeight = diskWeight;
    }

    /**
     * Scans system process table snapshots dynamically.
     * Captures essential system state processes across OS kernels.
     * Note: Since Java's ProcessHandle API has limited native CPU/RAM breakdown metrics,
     * we complement it with native OS diagnostics (e.g., ps/tasklist) when detailed telemetry is requested.
     */
    public Map<String, List<Map<String, Object>>> getTopConsumingProcesses(int limit) {
        List<Map<String, Object>> activeProcesses = new ArrayList<>();
        long currentPid = ProcessHandle.current().pid();

        try {
            // Check OS family to run appropriate native diagnostic stream
            String os = System.getProperty("os.name").toLowerCase();
            if (os.contains("win")) {
                activeProcesses = getWindowsProcesses();
            } else {
                activeProcesses = getUnixProcesses();
            }
        } catch (Exception e) {
            log.error("[SYSTEM ANALYZER ERROR] Failed to fetch OS process table snapshots: {}", e.getMessage());
        }

        // Mathematical sorting for resource profiling
        List<Map<String, Object>> topCpu = activeProcesses.stream()
                .sorted((p1, p2) -> Double.compare((double) p2.get("cpu"), (double) p1.get("cpu")))
                .limit(limit)
                .collect(Collectors.toList());

        List<Map<String, Object>> topMemory = activeProcesses.stream()
                .sorted((p1, p2) -> Double.compare((double) p2.get("memory"), (double) p1.get("memory")))
                .limit(limit)
                .collect(Collectors.toList());

        Map<String, List<Map<String, Object>>> profiles = new ConcurrentHashMap<>();
        profiles.put("top_cpu", topCpu);
        profiles.put("top_memory", topMemory);

        return profiles;
    }

    /**
     * Programmatic anti-freeze guard.
     * Evaluates current resource capacity. If thresholds breach 95%, non-critical process
     * lifecycles are targeted and safely terminated to prevent host lockups.
     */
    public List<Map<String, Object>> executeAntiFreezeGuard(double currentCpu, double currentRam, String nodeId, String location) {
        List<Map<String, Object>> mitigatedIncidents = new ArrayList<>();
        long selfPid = ProcessHandle.current().pid();

        // Trigger mitigation sequence if CPU or RAM breaches the safety margin of 95%
        if (currentCpu >= 95.0 || currentRam >= 95.0) {
            log.warn("[TICKET 5 ANTI-FREEZE]: Resource emergency triggered on {}. CPU: {}%, RAM: {}%", nodeId, currentCpu, currentRam);

            // Extract top resource hogs (limit to top 10 candidates)
            Map<String, List<Map<String, Object>>> profiles = getTopConsumingProcesses(10);
            List<Map<String, Object>> allOffenders = new ArrayList<>();
            allOffenders.addAll(profiles.getOrDefault("top_cpu", Collections.emptyList()));
            allOffenders.addAll(profiles.getOrDefault("top_memory", Collections.emptyList()));

            // Sort consolidated offenders by aggregate footprint (CPU + Memory) descending
            allOffenders.sort((o1, o2) -> {
                double total1 = (double) o1.get("cpu") + (double) o1.get("memory");
                double total2 = (double) o2.get("cpu") + (double) o2.get("memory");
                return Double.compare(total2, total1);
            });

            for (Map<String, Object> offender : allOffenders) {
                long pid = (long) offender.get("pid");
                String name = ((String) offender.get("name")).toLowerCase();

                // Guard: Ensure the application itself (or the JVM executing this code) is never targeted
                if (pid == selfPid || name.contains("java") || name.contains("javaw") || name.contains("gunicorn")) {
                    continue;
                }

                // Guard: Check against the critical processes whitelist
                boolean isWhitelisted = CRITICAL_PROCESS_WHITELIST.stream().anyMatch(name::contains);
                if (isWhitelisted) {
                    continue;
                }

                // Process Target Identified -> Initiate safe lifecycle termination
                Optional<ProcessHandle> liveProcess = ProcessHandle.of(pid);
                if (liveProcess.isPresent()) {
                    try {
                        log.warn("[TICKET 5 ANTI-FREEZE]: Targeting rogue process '{}' (PID: {}) to clear capacity spikes.", name, pid);
                        
                        // Forcefully terminate the process
                        liveProcess.get().destroyForcibly();

                        String alertMsg = String.format("Anti-Freeze Guard automatically terminated process '%s' (PID: %d) consuming CPU: %.1f%%, RAM: %.1f%% on node: %s",
                                name, pid, (double) offender.get("cpu"), (double) offender.get("memory"), nodeId);

                        Map<String, Object> incident = new HashMap<>();
                        incident.put("server", nodeId);
                        incident.put("location", location);
                        incident.put("message", alertMsg);
                        incident.put("level", "CRITICAL");
                        incident.put("timestamp", Instant.now().toString());

                        mitigatedIncidents.add(incident);
                        log.info("[TICKET 5 SUCCESS]: {}", alertMsg);
                        
                        // Terminate only the single heaviest rogue process per cycle to prevent over-killing the system
                        break;
                    } catch (Exception pErr) {
                        log.error("[TICKET 5 INTERRUPT]: Failed to intercept process {} (PID: {}): {}", name, pid, pErr.getMessage());
                    }
                }
            }
        }
        return mitigatedIncidents;
    }

    /**
     * Calculates the definitive infrastructure health index using a weighted balance algorithm.
     * Formula: Score = (100 - CPU)*W_cpu + (100 - RAM)*W_ram + (100 - Disk)*W_disk
     */
    public double calculateWeightedHealthScore(double cpuUsage, double ramUsage, double diskUsage) {
        double cpuFreeComponent = (100.0 - cpuUsage) * this.cpuWeight;
        double ramFreeComponent = (100.0 - ramUsage) * this.ramWeight;
        double diskFreeComponent = (100.0 - diskUsage) * this.diskWeight;

        double aggregatedScore = cpuFreeComponent + ramFreeComponent + diskFreeComponent;
        return Math.round(aggregatedScore * 10.0) / 10.0;
    }

    /**
     * Categorizes system operation states based on deterministic thresholds.
     */
    public String classifyHealthStatus(double healthScore) {
        if (healthScore >= 80.0) {
            return "Healthy";
        } else if (healthScore >= 60.0) {
            return "Warning";
        }
        return "Critical";
    }

    // ==============================================================================
    // OS-SPECIFIC NATIVE PROCESS EXTRACTORS
    // ==============================================================================

    private List<Map<String, Object>> getUnixProcesses() throws Exception {
        List<Map<String, Object>> processes = new ArrayList<>();
        // Execute 'ps' command to fetch PID, Process Name, %CPU, %MEM
        Process process = new ProcessBuilder("ps", "-ax", "-o", "pid,%cpu,%mem,comm").start();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            reader.readLine(); // Skip header
            while ((line = reader.readLine()) != null) {
                String[] tokens = line.trim().split("\\s+", 4);
                if (tokens.length >= 4) {
                    try {
                        long pid = Long.parseLong(tokens[0]);
                        double cpu = Double.parseDouble(tokens[1]);
                        double mem = Double.parseDouble(tokens[2]);
                        String name = tokens[3];

                        Map<String, Object> pInfo = new HashMap<>();
                        pInfo.put("pid", pid);
                        pInfo.put("name", name);
                        pInfo.put("cpu", cpu);
                        pInfo.put("memory", mem);
                        processes.add(pInfo);
                    } catch (NumberFormatException ignored) {}
                }
            }
        }
        return processes;
    }

    private List<Map<String, Object>> getWindowsProcesses() throws Exception {
        List<Map<String, Object>> processes = new ArrayList<>();
        // In Windows, we stream process list via tasklist command (Fallback basic parser)
        Process process = new ProcessBuilder("tasklist", "/FO", "CSV", "/NH").start();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                // Parse CSV formatted lines e.g. "cmd.exe","txt","1512"
                String[] tokens = line.replace("\"", "").split(",");
                if (tokens.length >= 5) {
                    try {
                        String name = tokens[0];
                        long pid = Long.parseLong(tokens[1]);
                        // Basic estimations for CPU/MEM on windows fallback stream
                        Map<String, Object> pInfo = new HashMap<>();
                        pInfo.put("pid", pid);
                        pInfo.put("name", name);
                        pInfo.put("cpu", 0.0); // Fallback placeholder
                        pInfo.put("memory", 0.1); // Fallback placeholder
                        processes.add(pInfo);
                    } catch (NumberFormatException ignored) {}
                }
            }
        }
        return processes;
    }
}