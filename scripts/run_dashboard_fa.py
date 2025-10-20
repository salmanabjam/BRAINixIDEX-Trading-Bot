"""
🚀 راه‌انداز داشبورد فارسی BiX TradeBOT
========================================
اجرای نسخه فارسی داشبورد با فونت وزیر
"""

import subprocess
import sys
from pathlib import Path

def main():
    """اجرای داشبورد فارسی"""
    
    print("=" * 70)
    print("🤖 BiX TradeBOT - داشبورد فارسی".center(70))
    print("=" * 70)
    print()
    
    # مسیر فایل داشبورد فارسی
    dashboard_path = Path(__file__).parent.parent / 'src' / 'ui' / 'dashboard_fa.py'
    
    if not dashboard_path.exists():
        print("❌ خطا: فایل داشبورد فارسی یافت نشد!")
        print(f"   مسیر: {dashboard_path}")
        return 1
    
    print("✅ فایل داشبورد یافت شد")
    print(f"📁 مسیر: {dashboard_path}")
    print()
    print("🚀 در حال راه‌اندازی...")
    print()
    print("📖 راهنما:")
    print("   - برای توقف: Ctrl+C")
    print("   - آدرس: http://localhost:8501")
    print()
    print("=" * 70)
    print()
    
    try:
        # اجرای streamlit
        subprocess.run([
            sys.executable, 
            '-m', 
            'streamlit', 
            'run', 
            str(dashboard_path)
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n\n✅ داشبورد با موفقیت متوقف شد")
        return 0
    
    except Exception as e:
        print(f"\n❌ خطا در اجرا: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
