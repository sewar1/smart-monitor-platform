import psutil
import time
import datetime
import socket
import requests
import os


# ==============================
# CONFIGURATION
# ==============================

CPU_THRESHOLD = 80
RAM_THRESHOLD = 80
DISK_THRESHOLD = 80

DISPLAY_INTERVAL = 2      # Real-time UI refresh
LOG_INTERVAL = 10         # Log every 10 seconds (DevOps style)

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

LOG_FILE = "system_log.txt"

last_log_time = 0


# ==============================
# UTIL: CREATE BAR
# ==============================

def create_bar(value, bars=30):
    """
    Creates visual progress bar for terminal UI
    """
    percent = value / 100
    filled = int(percent * bars)
    return "█" * filled + "-" * (bars - filled)


# ==============================
# SYSTEM METRICS
# ==============================

def get_system_usage():
    """
    Collects CPU, RAM, Disk usage + network stats
    """
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    net = psutil.net_io_counters()

    return cpu, ram, disk, net.bytes_sent, net.bytes_recv


# ==============================
# WARNINGS ENGINE
# ==============================

def check_warnings(cpu, ram, disk):
    """
    Checks system thresholds and returns alerts list
    """
    warnings = []

    if cpu > CPU_THRESHOLD:
        warnings.append("High CPU usage")

    if ram > RAM_THRESHOLD:
        warnings.append("High RAM usage")

    if disk > DISK_THRESHOLD:
        warnings.append("High Disk usage")

    return warnings


# ==============================
# TELEGRAM ALERT
# ==============================

def send_telegram_alert(message):
    """
    Sends alert to Telegram bot
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)


# ==============================
# LOG WRITER (OPTIMIZED)
# ==============================

def write_log(cpu, ram, disk, sent, recv, warnings):
    """
    Writes system snapshot to log file
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as file:
        file.write(
            f"[{timestamp}] CPU:{cpu:.2f}% RAM:{ram:.2f}% DISK:{disk:.2f}% "
            f"NET_SENT:{sent} NET_RECV:{recv}"
        )

        if warnings:
            file.write(" | WARNINGS: " + ", ".join(warnings))

        file.write("\n")


# ==============================
# LOG ANALYZER (LIGHT)
# ==============================

def analyze_logs():
    """
    Quick log analysis (warning counter)
    """
    if not os.path.exists(LOG_FILE):
        return

    warnings_count = 0

    with open(LOG_FILE, "r") as file:
        for line in file:
            if "WARNINGS" in line:
                warnings_count += 1

    print(f"📊 Warnings in logs: {warnings_count}")


# ==============================
# DISPLAY DASHBOARD (HTOP STYLE)
# ==============================

def display(cpu, ram, disk):
    """
    Real-time system dashboard (terminal UI)
    """
    hostname = socket.gethostname()

    print("\033c", end="")  # Clear screen

    print(f"📡 System Monitor - {hostname}")
    print("-" * 50)

    print(f"CPU  : |{create_bar(cpu)}| {cpu:.2f}%")
    print(f"RAM  : |{create_bar(ram)}| {ram:.2f}%")
    print(f"DISK : |{create_bar(disk)}| {disk:.2f}%")

    print("-" * 50)


# ==============================
# MAIN LOOP (ENGINE)
# ==============================

def main():
    global last_log_time

    print("🚀 Starting DevOps Monitoring System...")
    time.sleep(1)

    while True:
        # 1. Get system data
        cpu, ram, disk, sent, recv = get_system_usage()

        # 2. Display dashboard (real-time)
        display(cpu, ram, disk)

        # 3. Check warnings
        warnings = check_warnings(cpu, ram, disk)

        if warnings:
            print("⚠ ALERTS:", ", ".join(warnings))

            # Telegram alert
            send_telegram_alert("⚠ SYSTEM ALERT:\n" + "\n".join(warnings))

        # 4. Periodic logging (important optimization)
        current_time = time.time()

        if current_time - last_log_time >= LOG_INTERVAL:
            write_log(cpu, ram, disk, sent, recv, warnings)
            last_log_time = current_time

        # 5. Lightweight log analysis (optional insight)
        analyze_logs()

        # 6. Wait before refresh
        time.sleep(DISPLAY_INTERVAL)


# ==============================
# RUN PROGRAM
# ==============================

if __name__ == "__main__":
    main()