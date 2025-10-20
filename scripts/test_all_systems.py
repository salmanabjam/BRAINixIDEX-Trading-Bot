"""
🧪 Complete System Testing Script
Tests all components comprehensively
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from utils.system_simulator import SystemSimulator
from colorama import init, Fore, Style
import json

init(autoreset=True)

def print_header(text):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text:^70}")
    print(f"{Fore.CYAN}{'='*70}\n")

def print_test_result(test):
    """Print individual test result"""
    status_colors = {
        'PASS': Fore.GREEN,
        'FAIL': Fore.RED,
        'WARN': Fore.YELLOW,
        'SKIP': Fore.MAGENTA
    }
    
    status = test['status']
    color = status_colors.get(status, Fore.WHITE)
    icon = '✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️' if status == 'WARN' else '⏭️'
    
    print(f"{icon} {color}{test['name']:<20}{Style.RESET_ALL} {status:<6} ({test['duration']:.2f}s)")
    print(f"   {Fore.WHITE}{test['message']}{Style.RESET_ALL}")
    
    # Print key details
    if test['details']:
        for key, value in list(test['details'].items())[:5]:  # Show first 5 details
            if isinstance(value, (str, int, float)):
                print(f"   {Fore.CYAN}• {key}: {Fore.WHITE}{value}{Style.RESET_ALL}")
            elif isinstance(value, dict) and len(value) <= 3:
                print(f"   {Fore.CYAN}• {key}:{Style.RESET_ALL}")
                for k, v in value.items():
                    print(f"     {Fore.YELLOW}- {k}: {Fore.WHITE}{v}{Style.RESET_ALL}")
    
    # Print error if failed
    if status == 'FAIL' and 'error' in test['details']:
        print(f"   {Fore.RED}ERROR: {test['details']['error']}{Style.RESET_ALL}")
    
    print()

def print_summary(summary):
    """Print test summary"""
    print_header("📊 TEST SUMMARY")
    
    total = summary['total_tests']
    passed = summary['passed']
    failed = summary['failed']
    warnings = summary['warnings']
    skipped = summary['skipped']
    success_rate = summary['success_rate']
    
    print(f"{Fore.CYAN}Total Tests:    {Fore.WHITE}{total}")
    print(f"{Fore.GREEN}✅ Passed:      {Fore.WHITE}{passed}")
    print(f"{Fore.RED}❌ Failed:      {Fore.WHITE}{failed}")
    print(f"{Fore.YELLOW}⚠️  Warnings:    {Fore.WHITE}{warnings}")
    print(f"{Fore.MAGENTA}⏭️  Skipped:     {Fore.WHITE}{skipped}")
    print(f"{Fore.CYAN}Duration:       {Fore.WHITE}{summary['total_duration']:.2f}s")
    
    # Success rate with color
    if success_rate >= 90:
        color = Fore.GREEN
        verdict = "EXCELLENT ✨"
    elif success_rate >= 75:
        color = Fore.YELLOW
        verdict = "GOOD 👍"
    elif success_rate >= 50:
        color = Fore.YELLOW
        verdict = "NEEDS IMPROVEMENT ⚠️"
    else:
        color = Fore.RED
        verdict = "CRITICAL ❌"
    
    print(f"\n{color}Success Rate:   {success_rate:.1f}% - {verdict}{Style.RESET_ALL}\n")

def main():
    """Run all system tests"""
    print_header("🧪 BRAINixIDEX Trading Bot - Complete System Test")
    
    print(f"{Fore.YELLOW}Starting comprehensive system testing...{Style.RESET_ALL}\n")
    
    # Initialize simulator
    simulator = SystemSimulator()
    
    # Run all tests
    print(f"{Fore.CYAN}Running 8 comprehensive tests...{Style.RESET_ALL}\n")
    results = simulator.run_all_tests()
    
    # Print individual test results
    print_header("📋 DETAILED TEST RESULTS")
    
    for test in results['tests']:
        print_test_result(test)
    
    # Print summary
    print_summary(results['summary'])
    
    # Save detailed report
    report_file = project_root / 'logs' / 'system_test_report.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"{Fore.GREEN}✅ Detailed report saved to: {report_file}{Style.RESET_ALL}\n")
    
    # Generate text report
    text_report = simulator.generate_report(results)
    
    report_txt = project_root / 'logs' / 'system_test_report.txt'
    with open(report_txt, 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    print(f"{Fore.GREEN}✅ Text report saved to: {report_txt}{Style.RESET_ALL}\n")
    
    # Final verdict
    if results['summary']['success_rate'] >= 90:
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}🎉 ALL SYSTEMS OPERATIONAL - Ready for Trading! 🚀")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
        return 0
    elif results['summary']['failed'] > 0:
        print(f"{Fore.RED}{'='*70}")
        print(f"{Fore.RED}⚠️  CRITICAL ERRORS FOUND - Please fix failed tests")
        print(f"{Fore.RED}{'='*70}{Style.RESET_ALL}\n")
        return 1
    else:
        print(f"{Fore.YELLOW}{'='*70}")
        print(f"{Fore.YELLOW}⚠️  SOME WARNINGS - Review before trading")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
        return 0

if __name__ == "__main__":
    exit(main())
