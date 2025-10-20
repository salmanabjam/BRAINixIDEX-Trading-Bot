# 🗑️ حذف فایل‌های اضافی و غیرضروری

Write-Host "🔍 شناسایی فایل‌های اضافی..." -ForegroundColor Yellow

# فایل‌های اضافی که استفاده نمی‌شوند
$unusedFiles = @(
    # فایل‌های تست و موقت
    "ai_analysis_report.json",
    "backtest_chart.html",
    "model_preference.json",
    
    # فایل‌های قدیمی که جایگزین شده‌اند
    "RUNNING.md",              # جایگزین: START_HERE.md
    "SYSTEM_SUMMARY.md",       # جایگزین: EXECUTIVE_SUMMARY.md
    "SYSTEM_ARCHITECTURE.txt", # جایگزین: COMPLETE_CHANGES_REPORT.md
    "README.md",               # جایگزین: README_NEW.md
    
    # اسکریپت‌های قدیمی
    "train_fresh.py",          # عملکرد در dashboard.py تعبیه شده
    "train_model.py",          # عملکرد در dashboard.py تعبیه شده
    "run.ps1",                 # دیگر نیازی نیست
    "setup.ps1",               # یکبار استفاده شده
    "setup.sh"                 # برای لینوکس، در ویندوز نیازی نیست
)

Write-Host "`n📋 فایل‌های شناسایی شده برای حذف:" -ForegroundColor Cyan
foreach ($file in $unusedFiles) {
    if (Test-Path $file) {
        Write-Host "  ❌ $file" -ForegroundColor Red
    } else {
        Write-Host "  ⚠️  $file (وجود ندارد)" -ForegroundColor DarkGray
    }
}

Write-Host "`n⚠️  هشدار: این فایل‌ها حذف خواهند شد!" -ForegroundColor Yellow
Write-Host "آیا می‌خواهید ادامه دهید؟ (Y/N): " -NoNewline
$confirmation = Read-Host

if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
    Write-Host "`n🗑️  در حال حذف فایل‌ها..." -ForegroundColor Yellow
    
    $deletedCount = 0
    $notFoundCount = 0
    
    foreach ($file in $unusedFiles) {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Host "  ✅ حذف شد: $file" -ForegroundColor Green
            $deletedCount++
        } else {
            $notFoundCount++
        }
    }
    
    Write-Host "`n📊 نتیجه:" -ForegroundColor Cyan
    Write-Host "  ✅ حذف شده: $deletedCount فایل" -ForegroundColor Green
    Write-Host "  ⚠️  یافت نشد: $notFoundCount فایل" -ForegroundColor DarkGray
    
    Write-Host "`n✅ تمیزسازی با موفقیت انجام شد!" -ForegroundColor Green
    
} else {
    Write-Host "`n❌ عملیات لغو شد." -ForegroundColor Red
}

Write-Host "`n💡 نکته: فایل‌های زیر حفظ شده‌اند:" -ForegroundColor Cyan
Write-Host "  ✅ README_NEW.md (مستندات اصلی)" -ForegroundColor Green
Write-Host "  ✅ START_HERE.md (راهنمای شروع)" -ForegroundColor Green
Write-Host "  ✅ FINAL_GUIDE.md (راهنمای کامل)" -ForegroundColor Green
Write-Host "  ✅ تمام فایل‌های .py (کدهای اصلی)" -ForegroundColor Green
