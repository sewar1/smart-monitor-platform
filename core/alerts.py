from core.logger import log_alert


def check_alerts(nodes):
    """
    Evaluates system metrics against thresholds.
    Returns a list of warning messages.
    """

    alerts = []

    for node in nodes:

        if node["cpu"] > 85:

            message = (
                f"{node['name']} - HIGH CPU USAGE: "
                f"{node['cpu']:.1f}%"
            )

            alerts.append(message)

            log_alert(message)

        if node["ram"] > 85:

            message = (
                f"{node['name']} - HIGH RAM USAGE: "
                f"{node['ram']:.1f}%"
            )

            alerts.append(message)

            log_alert(message)

        if node["disk"] > 90:

            message = (
                f"{node['name']} - HIGH DISK USAGE: "
                f"{node['disk']:.1f}%"
            )

            alerts.append(message)

            log_alert(message)

    return alerts