import React, { useState, useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';
import { Navbar } from './components/Navbar';
import { ServerNodeSelector } from './components/ServerNodeSelector';
import { AlertBanner } from './components/AlertBanner';
import { MetricsGrid } from './components/MetricsGrid';
import { TelemetryPanels } from './components/TelemetryPanels';
import { OperatorDirectory } from './components/OperatorDirectory';

// Explicit type-only imports to satisfy the strict 'verbatimModuleSyntax' rules
import type { ServerNodeKey } from './components/ServerNodeSelector';
import type { SystemProcess, IncidentLog } from './components/TelemetryPanels';
import type { Operator } from './components/OperatorDirectory';

// Register Chart.js modules safely in the React environment
Chart.register(...registerables);

// =========================================================================
// 1. i18n TRANSLATION MATRIX DEFINITIONS (Preserving English & German)
// =========================================================================
const dashboardTranslations = {
  en: {
    navTitle: "SMART MONITOR PLATFORM",
    tabTelemetry: "Telemetry Metrics",
    tabDirectory: "User Directory",
    bannerAlert: "CRITICAL INFRASTRUCTURE EVENT DETECTED",
    lblCpu: "Processor Load",
    lblRam: "Memory Pools",
    lblDisk: "Storage Block",
    lblMatrix: "Weighted Health Matrix",
    hdrIncidents: "Active Incident Log",
    hdrCpuThreads: "Thread Profiling (Top CPU)",
    hdrRamPages: "Page Descriptors (Top RAM)",
    hdrLedger: "SQL Persistent Ledger Logs (Recent Alert History)",
    hdrChart: "Live Stream Telemetry Waveform Analyzer",
    hdrDirectoryTitle: "Authorized System Operator Directory",
    lblTotalUsers: "Active Node Operators",
    thCpuDesc: "Process Descriptor",
    thCpuLoad: "CPU Load",
    thRamDesc: "Process Descriptor",
    thRamBase: "Memory Base",
    thDirId: "Operator Identifier",
    thDirIdentity: "Identity Node String",
    thDirRole: "Access Authorization Role",
    thDirStatus: "Status",
    thDirActions: "Operational Actions",
    btnActionModify: "Edit Role",
    btnActionSuspend: "Revoke",
    modalActionTitle: "Modify Operator Clearance",
    modalActionBody: "Update access credentials structural token permissions for node operator: ",
    modalRoleSelectLabel: "Select Target Security clearance Level",
    btnModalCancel: "Abort",
    btnModalConfirm: "Execute Vector",
    lblOperationalNormal: "Node operational thresholds normal.",
    lblWaitingHistory: "Waiting for historical system traces...",
    langBtn: "DE"
  },
  de: {
    navTitle: "INTELLIGENTE MONITOR-PLATTFORM",
    tabTelemetry: "Telemetrie-Metriken",
    tabDirectory: "Benutzerverzeichnis",
    bannerAlert: "KRITISCHES INFRASTRUKTUR-EREIGNIS ERKANNT",
    lblCpu: "Prozessorlast",
    lblRam: "Speicher-Pools",
    lblDisk: "Speicherblock",
    lblMatrix: "Gewichtete Gesundheitsmatrix",
    hdrIncidents: "Aktives Ereignisprotokoll",
    hdrCpuThreads: "Thread-Profilierung (Top CPU)",
    hdrRamPages: "Seiten-Deskriptoren (Top RAM)",
    hdrLedger: "Persistente SQL-Ledger-Protokolle (Letzte Alarme)",
    hdrChart: "Live-Stream Telemetrie Wellenformanalysator",
    hdrDirectoryTitle: "Autorisiertes Systemoperator-Verzeichnis",
    lblTotalUsers: "Aktive Knoten-Operatoren",
    thCpuDesc: "Prozess-Deskriptor",
    thCpuLoad: "CPU-Last",
    thRamDesc: "Prozess-Deskriptor",
    thRamBase: "Speicherbasis",
    thDirId: "Operator-Bezeichner",
    thDirIdentity: "Identitätsknoten-String",
    thDirRole: "Zugriffsautorisierungsrolle",
    thDirStatus: "Status",
    thDirActions: "Operationelle Aktionen",
    btnActionModify: "Rolle ändern",
    btnActionSuspend: "Widerrufen",
    modalActionTitle: "Operator-Kontext ändern",
    modalActionBody: "Sicherheitsfreigabezertifikate kündigen und Operator löschen: ",
    modalRoleSelectLabel: "Wählen Sie die Sicherheitsfreigabestufe",
    btnModalCancel: "Abbrechen",
    btnModalConfirm: "Vektor ausführen",
    lblOperationalNormal: "Knotenbetriebsschwellenwerte normal.",
    lblWaitingHistory: "Warten auf historische Systemspuren...",
    langBtn: "EN"
  }
};

interface NodeTelemetryHistory {
  labels: string[];
  cpu: number[];
  ram: number[];
  disk: number[];
}

export const Dashboard: React.FC = () => {
  // Check auth credentials immediately on component mount (Local Security Firewall Gate)
  useEffect(() => {
    if (!localStorage.getItem('monitor_jwt_token')) {
      window.location.href = '/login';
    }
  }, []);

  // Helper function for secure authorization headers matching Backend spec
  const getAuthHeaders = (): Record<string, string> => {
    return {
      'Authorization': `Bearer ${localStorage.getItem('monitor_jwt_token')}`,
      'Content-Type': 'application/json'
    };
  };

  const executeSecureLogout = () => {
    localStorage.removeItem('monitor_jwt_token');
    window.location.href = '/login';
  };

  // =========================================================================
  // 2. STATE CONFIGURATIONS
  // =========================================================================
  const [activeTab, setActiveTab] = useState<'telemetry' | 'directory'>('telemetry');
  const [activeNode, setActiveNode] = useState<ServerNodeKey>('Docker_Production_Container');
  const [currentLang, setCurrentLang] = useState<'en' | 'de'>('en');

  // Node telemetry stats
  const [cpuValue, setCpuValue] = useState<number>(0);
  const [ramValue, setRamValue] = useState<number>(0);
  const [diskValue, setDiskValue] = useState<number>(0);
  const [healthScore, setHealthScore] = useState<number>(100);
  const [healthStatusText, setHealthStatusText] = useState<string>("Analyzing Matrix");
  const [healthSeverity, setHealthSeverity] = useState<'healthy' | 'warning' | 'critical'>('healthy');
  
  // Incidents & Logs
  const [activeIncidents, setActiveIncidents] = useState<IncidentLog[]>([]);
  const [archivedIncidents, setArchivedIncidents] = useState<IncidentLog[]>([]);
  const [isAlertVisible, setIsAlertVisible] = useState<boolean>(false);
  const [alertTimestamp, setAlertTimestamp] = useState<string>("00:00:00");

  // Thread and Page profiling tables
  const [cpuProcesses, setCpuProcesses] = useState<SystemProcess[]>([]);
  const [ramProcesses, setRamProcesses] = useState<SystemProcess[]>([]);

  // Directory operators and modal behaviors
  const [operators, setOperators] = useState<Operator[]>([]);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedOperator, setSelectedOperator] = useState<Operator | null>(null);
  const [modalTargetRole, setModalTargetRole] = useState<'Admin' | 'DevSecOps' | 'Operator'>('Operator');
  const [activeActionType, setActiveActionType] = useState<'UPDATE_ROLE' | 'REVOKE_ACCESS' | null>(null);

  // Persistence trace matrices for the 3-line chart stream
  const maxChartPoints = 30;
  const nodeHistoryRef = useRef<Record<ServerNodeKey, NodeTelemetryHistory>>({
    Docker_Production_Container: { labels: [], cpu: [], ram: [], disk: [] },
    Windows_Host: { labels: [], cpu: [], ram: [], disk: [] },
    VMware_Ubuntu: { labels: [], cpu: [], ram: [], disk: [] }
  });

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartInstanceRef = useRef<Chart | null>(null);

  const t = dashboardTranslations[currentLang];

  // =========================================================================
  // 3. CHART.JS LIFE CYCLE MANAGEMENT
  // =========================================================================
  const initializeWaveformChart = () => {
    if (!canvasRef.current) return;
    const history = nodeHistoryRef.current[activeNode];

    if (chartInstanceRef.current) {
      chartInstanceRef.current.data.labels = history.labels;
      chartInstanceRef.current.data.datasets[0].data = history.cpu;
      chartInstanceRef.current.data.datasets[1].data = history.ram;
      chartInstanceRef.current.data.datasets[2].data = history.disk;
      chartInstanceRef.current.update('none');
      return;
    }

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    chartInstanceRef.current = new Chart(ctx, {
      type: "line",
      data: {
        labels: history.labels,
        datasets: [
          { label: "CPU Matrix %", borderColor: "#ef4444", backgroundColor: "rgba(239, 68, 68, 0.04)", data: history.cpu, tension: 0.25, fill: true, pointRadius: 0 },
          { label: "RAM Allocation %", borderColor: "#3b82f6", backgroundColor: "rgba(59, 130, 246, 0.04)", data: history.ram, tension: 0.25, fill: true, pointRadius: 0 },
          { label: "Block Disk Storage %", borderColor: "#10b981", backgroundColor: "rgba(16, 185, 129, 0.04)", data: history.disk, tension: 0.25, fill: true, pointRadius: 0 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: { legend: { labels: { color: '#94a3b8', font: { weight: 600 } } } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.01)' }, ticks: { color: '#64748b' } },
          y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.01)' }, ticks: { color: '#64748b' } }
        }
      }
    });
  };

  // Re-draw chart on canvas mounts or node changes
  useEffect(() => {
    if (activeTab === 'telemetry') {
      initializeWaveformChart();
    }
  }, [activeNode, activeTab]);

  // =========================================================================
  // 4. API INGESTION LOOP (TELEMETRY PIPELINE)
  // =========================================================================
  const fetchNodeTelemetry = async () => {
    if (activeTab !== 'telemetry') return;

    try {
      const response = await fetch(`/api/metrics?node_id=${encodeURIComponent(activeNode)}`, {
        method: 'GET',
        headers: getAuthHeaders()
      });

      if (response.status === 401) {
        executeSecureLogout();
        return;
      }

      if (!response.ok) throw new Error("Backend pipeline error");
      let data = await response.json();
      const nodesArray = data.nodes || data;

      // Fallback Mock Engine in case database has clean traces
      if (!nodesArray || nodesArray.length === 0 || !nodesArray[0].cpu_usage) {
        let baseCpu = activeNode === "Windows_Host" ? 25 : (activeNode === "VMware_Ubuntu" ? 65 : 45);
        let baseRam = activeNode === "Windows_Host" ? 40 : (activeNode === "VMware_Ubuntu" ? 75 : 60);

        const mockNode = {
          node_id: activeNode,
          cpu_usage: Math.min(100, Math.max(5, Math.floor(baseCpu + (Math.random() * 20 - 10)))),
          ram_usage: Math.min(100, Math.max(5, Math.floor(baseRam + (Math.random() * 10 - 5)))),
          disk_usage: activeNode === "Windows_Host" ? 58 : (activeNode === "VMware_Ubuntu" ? 81 : 34),
          top_processes: [
            { "pid": 1240, "name": `${activeNode}_daemon`, "cpu": 4.2, "memory": 12.4 },
            { "pid": 3120, "name": "telemetry_worker", "cpu": 1.8, "memory": 2.1 }
          ]
        };

        data = {
          nodes: [mockNode],
          health: {
            score: Math.floor(85 + (Math.random() * 15)),
            status: "Healthy"
          }
        };
      }

      const node = data.nodes[0];
      setCpuValue(Number(node.cpu_usage.toFixed(1)));
      setRamValue(Number(node.ram_usage.toFixed(1)));
      setDiskValue(Number(node.disk_usage.toFixed(1)));

      // Health Matrix score determination
      const derivedScore = data.health ? data.health.score : Number((100 - (node.cpu_usage + node.ram_usage) / 2).toFixed(0));
      const statusText = data.health ? data.health.status : (derivedScore > 50 ? "Healthy" : "Critical");
      setHealthScore(derivedScore);
      setHealthStatusText(statusText);

      if (statusText === "Warning") setHealthSeverity("warning");
      else if (statusText === "Critical") setHealthSeverity("critical");
      else setHealthSeverity("healthy");

      // Set Incidents banner display state
      const activeAlerts = data.alerts || [];
      setIsAlertVisible(activeAlerts.length > 0);
      if (activeAlerts.length > 0) {
        setAlertTimestamp(new Date().toLocaleTimeString());
        setActiveIncidents(activeAlerts.map((msg: string, idx: number) => ({ id: idx, message: msg })));
      } else {
        setActiveIncidents([]);
      }

      // Map ranking process arrays
      if (node.top_processes && node.top_processes.length > 0) {
        setCpuProcesses(node.top_processes.map((p: any, idx: number) => ({
          id: p.pid || idx,
          descriptor: `${p.name || 'Unknown'} (${p.pid})`,
          metricValue: `${p.cpu ? p.cpu.toFixed(1) : "0.0"}%`
        })));
        setRamProcesses(node.top_processes.map((p: any, idx: number) => ({
          id: p.pid || idx,
          descriptor: `${p.name || 'Unknown'} (${p.pid})`,
          metricValue: `${p.memory ? p.memory.toFixed(1) : "0.0"}%`
        })));
      } else {
        setCpuProcesses([]);
        setRamProcesses([]);
      }

      // Feed historical memory trace buffers
      const time = node.last_seen ? node.last_seen.split(" ")[1] : new Date().toLocaleTimeString();
      const history = nodeHistoryRef.current[activeNode];
      history.labels.push(time);
      history.cpu.push(node.cpu_usage);
      history.ram.push(node.ram_usage);
      history.disk.push(node.disk_usage);

      if (history.labels.length > maxChartPoints) {
        history.labels.shift();
        history.cpu.shift();
        history.ram.shift();
        history.disk.shift();
      }

      if (chartInstanceRef.current) {
        chartInstanceRef.current.update('none');
      }

    } catch (error) {
      console.error("Telemetry ingest interface crash:", error);
    }
  };

  const fetchAlertHistory = async () => {
    if (activeTab !== 'telemetry') return;

    try {
      const response = await fetch(`/api/alerts/history?agent=${encodeURIComponent(activeNode)}`, {
        method: "GET",
        headers: getAuthHeaders()
      });

      if (response.status === 401) {
        executeSecureLogout();
        return;
      }

      const json = await response.json();
      if (json.history && json.history.length > 0) {
        setArchivedIncidents(json.history.reverse().map((log: string, idx: number) => ({
          id: idx,
          message: log
        })));
      } else {
        setArchivedIncidents([]);
      }
    } catch (error) {
      console.error("Ledger sync matrix error:", error);
    }
  };

  // =========================================================================
  // 5. CORPORATE DIRECTORY PIPELINE CONTROLLERS (RBAC MATRIX)
  // =========================================================================
  const fetchUserDirectory = async () => {
    if (activeTab !== 'directory') return;

    try {
      const response = await fetch("/api/users", { 
        method: "GET", 
        headers: getAuthHeaders() 
      });

      if (response.status === 401) {
        executeSecureLogout();
        return;
      }

      const data = await response.json();
      
      if (data.users && data.users.length > 0) {
        setOperators(data.users.map((user: any) => ({
          id: user.id,
          identityString: user.username,
          role: user.role || 'Operator',
          status: 'Active' // Mapping fallback state for layout
        })));
      } else {
        setOperators([]);
      }
    } catch (error) {
      console.error("Failed to map target directory streams safely:", error);
    }
  };

  // Automated scheduling loop setups
  useEffect(() => {
    fetchNodeTelemetry();
    fetchAlertHistory();

    const telemetryInterval = setInterval(fetchNodeTelemetry, 5000);
    const alertInterval = setInterval(fetchAlertHistory, 10000);

    return () => {
      clearInterval(telemetryInterval);
      clearInterval(alertInterval);
    };
  }, [activeNode, activeTab]);

  useEffect(() => {
    if (activeTab === 'directory') {
      fetchUserDirectory();
    }
  }, [activeTab]);

  // =========================================================================
  // 6. ADMINISTRATIVE HANDLERS (RBAC INTERFACES & MODALS)
  // =========================================================================
  const handleOpenModal = (operator: Operator, actionType: 'role' | 'suspend') => {
    setSelectedOperator(operator);
    setModalTargetRole(operator.role);
    setIsModalOpen(true);
    setActiveActionType(actionType === 'role' ? 'UPDATE_ROLE' : 'REVOKE_ACCESS');
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedOperator(null);
    setActiveActionType(null);
  };

  const handleExecuteAction = async () => {
    if (!selectedOperator || !activeActionType) return;

    let url = `/api/users/${selectedOperator.id}`;
    let method = "DELETE"; 
    let payload = {};

    if (activeActionType === "UPDATE_ROLE") {
      method = "PUT";
      payload = { role: modalTargetRole };
    }

    try {
      const response = await fetch(url, {
        method: method,
        headers: getAuthHeaders(),
        body: activeActionType === "UPDATE_ROLE" ? JSON.stringify(payload) : null
      });

      if (response.ok) {
        handleCloseModal();
        fetchUserDirectory();
      } else {
        alert("Administrative execution vector failed. Check structural logs.");
      }
    } catch (error) {
      console.error("Vector routing tracking collapse:", error);
    }
  };

  // Node display string formatting
  const getNodeDisplayLabel = () => {
    if (activeNode === "Docker_Production_Container") return "NODE: Docker Node (Ludwigshafen)";
    if (activeNode === "Windows_Host") return "NODE: Windows Host (Mannheim)";
    return "NODE: VMware Linux (Heidelberg)";
  };

  const getHeartbeatState = () => {
    if (activeNode === "Docker_Production_Container") return "red";
    if (activeNode === "Windows_Host") return "blue";
    return "green";
  };

  return (
    <div className="min-h-screen bg-[#070a13] text-[#f8fafc] font-sans overflow-x-hidden pb-12">
      {/* 1. Navbar Portal Container */}
      <Navbar
        activeTab={activeTab}
        onTabChange={(tab) => setActiveTab(tab)}
        currentLang={currentLang}
        onToggleLanguage={() => setCurrentLang(currentLang === 'en' ? 'de' : 'en')}
        onLogout={executeSecureLogout}
        translations={{
          navTitle: t.navTitle,
          tabTelemetry: t.tabTelemetry,
          tabDirectory: t.tabDirectory,
          langBtn: t.langBtn,
        }}
      />

      <div className="container-fluid px-8 py-6">
        
        {/* 2. Server Node Switcher */}
        <ServerNodeSelector
          activeNode={activeNode}
          onNodeChange={(node) => {
            setActiveNode(node);
            initializeWaveformChart();
          }}
          nodeDisplayLabel={getNodeDisplayLabel()}
          heartbeatState={getHeartbeatState()}
        />

        {/* 3. Incident Alert Banner */}
        <AlertBanner
          isVisible={isAlertVisible}
          alertText={t.bannerAlert}
          timestamp={alertTimestamp}
        />

        {/* 4. Tab Routing Conditional Panes */}
        {activeTab === 'telemetry' ? (
          <>
            {/* Real-time Hardware Metrics Grid */}
            <MetricsGrid
              cpuValue={cpuValue}
              ramValue={ramValue}
              diskValue={diskValue}
              healthScore={healthScore}
              healthStatusText={healthStatusText}
              healthStatusSeverity={healthSeverity}
              translations={{
                lblCpu: t.lblCpu,
                lblRam: t.lblRam,
                lblDisk: t.lblDisk,
                lblMatrix: t.lblMatrix,
              }}
            />

            {/* Consoles, Process tables, and Chart wave analyzer */}
            <TelemetryPanels
              isVisible={activeTab === 'telemetry'}
              activeIncidents={activeIncidents}
              archivedIncidents={archivedIncidents}
              cpuProcesses={cpuProcesses}
              ramProcesses={ramProcesses}
              canvasRef={canvasRef}
              translations={{
                hdrIncidents: t.hdrIncidents,
                hdrCpuThreads: t.hdrCpuThreads,
                hdrRamPages: t.hdrRamPages,
                hdrLedger: t.hdrLedger,
                hdrChart: t.hdrChart,
                thCpuDesc: t.thCpuDesc,
                thCpuLoad: t.thCpuLoad,
                thRamDesc: t.thRamDesc,
                thRamBase: t.thRamBase,
                lblOperationalNormal: t.lblOperationalNormal,
                lblWaitingHistory: t.lblWaitingHistory,
              }}
            />
          </>
        ) : (
          /* 5. Operator Control Directory & Role modifier */
          <OperatorDirectory
            isVisible={activeTab === 'directory'}
            operators={operators}
            translations={{
              hdrDirectoryTitle: t.hdrDirectoryTitle,
              lblTotalUsers: t.lblTotalUsers,
              thDirId: t.thDirId,
              thDirIdentity: t.thDirIdentity,
              thDirRole: t.thDirRole,
              thDirStatus: t.thDirStatus,
              thDirActions: t.thDirActions,
              btnActionModify: t.btnActionModify,
              btnActionSuspend: t.btnActionSuspend,
              modalActionTitle: t.modalActionTitle,
              modalActionBody: t.modalActionBody,
              modalRoleSelectLabel: t.modalRoleSelectLabel,
              btnModalCancel: t.btnModalCancel,
              btnModalConfirm: t.btnModalConfirm,
            }}
            isModalOpen={isModalOpen}
            selectedOperator={selectedOperator}
            modalTargetRole={modalTargetRole}
            onOpenModal={handleOpenModal}
            onCloseModal={handleCloseModal}
            onTargetRoleChange={(role) => setModalTargetRole(role)}
            onExecuteAction={handleExecuteAction}
          />
        )}

      </div>
    </div>
  );
};