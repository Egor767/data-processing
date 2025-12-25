from datetime import datetime
import os
from pathlib import Path

from data_pipeline.src.db import (
    call_fn_dq_checks_load,
    get_dq_results_last_run,
    get_dq_summary,
    check_dq_status
)


def send_alert(message: str):
    project_root = Path(__file__).parent.parent
    log_file = project_root / "src" / "logs.txt"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_msg = f"[{timestamp}] Critical error: {message}\n"

    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(alert_msg)

    print(f"Alert has been written: {log_file.absolute()}")


def checks(date_start="2023-01-01", date_end="2025-01-01"):
    print("Running Data Quality checks...")

    success, message = call_fn_dq_checks_load(date_start, date_end)
    print(f"{message}")

    df_results, run_info = get_dq_results_last_run()
    print(f"\n Last checks ({run_info}):")
    if not df_results.empty:
        print(df_results.to_string(index=False))

    summary = get_dq_summary()
    total = summary['total_checks']
    failed = summary['failed']
    failed_pct = (failed / total * 100) if total > 0 else 0

    print(f"\n Result: {total} проверок")
    print(f"Passed: {summary['passed']} ({100 - failed_pct:.1f}%)")
    print(f"Failed: {failed}")
    print(f"Errors: {summary['errors']}")

    if failed_pct > 30:
        alert_msg = f"{failed_pct:.1f}% checks not passed ({failed}/{total})"
        send_alert(alert_msg)
        print(f"Critical alert: {alert_msg}")
    else:
        print("Data Quality is normal")

    status_ok, status_msg = check_dq_status()
    print(f"\n Status: {status_msg}")
    print("Data Quality checks completed!")
