"""
BiX TradeBOT - Dashboard Launcher
==================================
لانچر ساده برای اجرای داشبورد نهایی

نویسنده: SALMAN ThinkTank AI Core
نسخه: 2.0.0
"""

import subprocess
import sys
from pathlib import Path

def main():
    """اجرای داشبورد نهایی"""
    
    # مسیر داشبورد
    dashboard_path = Path(__file__).parent / "src" / "ui" / "dashboard.py"
    
    # دستور اجرا
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard_path),
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    print("🚀 در حال اجرای BiX TradeBOT Ultimate Dashboard...")
    print(f"📂 مسیر: {dashboard_path}")
    print(f"🌐 URL: http://localhost:8501")
    print("-" * 60)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n⏹️ داشبورد متوقف شد.")
    except Exception as e:
        print(f"❌ خطا: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
