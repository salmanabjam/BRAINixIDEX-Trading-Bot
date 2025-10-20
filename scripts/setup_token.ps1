# 🔑 اسکریپت تنظیم خودکار توکن‌ها
# برای: @salmanabjam

param(
    [string]$Service,
    [string]$Token
)

Write-Host "`n🔑 تنظیم خودکار توکن برای $Service" -ForegroundColor Cyan

# تابع تنظیم توکن
function Set-APIToken {
    param(
        [string]$ServiceName,
        [string]$EnvVarName,
        [string]$TokenValue
    )
    
    Write-Host "`n📝 در حال تنظیم $ServiceName..." -ForegroundColor Yellow
    
    # تنظیم در Windows Environment Variables
    [System.Environment]::SetEnvironmentVariable($EnvVarName, $TokenValue, [System.EnvironmentVariableTarget]::User)
    
    # تنظیم در Session فعلی
    Set-Item -Path "Env:$EnvVarName" -Value $TokenValue
    
    Write-Host "✅ $ServiceName تنظیم شد!" -ForegroundColor Green
    
    # نمایش 20 کاراکتر اول
    $preview = $TokenValue.Substring(0, [Math]::Min(20, $TokenValue.Length))
    Write-Host "   پیش‌نمایش: $preview..." -ForegroundColor DarkGray
}

# تابع تست توکن
function Test-APIToken {
    param([string]$ServiceName)
    
    Write-Host "`n🧪 در حال تست $ServiceName..." -ForegroundColor Yellow
    
    switch ($ServiceName) {
        "GitHub" {
            $token = $env:GITHUB_TOKEN
            if ($token) {
                try {
                    $headers = @{
                        "Authorization" = "Bearer $token"
                        "Accept" = "application/vnd.github.v3+json"
                    }
                    $response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -Method Get
                    Write-Host "✅ GitHub OK - User: $($response.login)" -ForegroundColor Green
                    return $true
                } catch {
                    Write-Host "❌ GitHub Error: $_" -ForegroundColor Red
                    return $false
                }
            }
        }
        
        "Google" {
            $key = $env:GOOGLE_API_KEY
            if ($key) {
                try {
                    $url = "https://generativelanguage.googleapis.com/v1beta/models?key=$key"
                    $response = Invoke-RestMethod -Uri $url -Method Get
                    Write-Host "✅ Google Gemini OK - Models: $($response.models.Count)" -ForegroundColor Green
                    return $true
                } catch {
                    Write-Host "❌ Google Error: $_" -ForegroundColor Red
                    return $false
                }
            }
        }
        
        "HuggingFace" {
            $token = $env:HUGGINGFACE_TOKEN
            if ($token) {
                try {
                    $headers = @{ "Authorization" = "Bearer $token" }
                    $response = Invoke-RestMethod -Uri "https://huggingface.co/api/whoami-v2" -Headers $headers -Method Get
                    Write-Host "✅ Hugging Face OK - User: $($response.name)" -ForegroundColor Green
                    return $true
                } catch {
                    Write-Host "❌ Hugging Face Error: $_" -ForegroundColor Red
                    return $false
                }
            }
        }
        
        "OpenAI" {
            Write-Host "⚠️  OpenAI نیاز به تست Python دارد" -ForegroundColor Yellow
            return $true
        }
        
        "Anthropic" {
            Write-Host "⚠️  Anthropic نیاز به تست Python دارد" -ForegroundColor Yellow
            return $true
        }
    }
    
    Write-Host "⚠️  توکن تنظیم نشده است" -ForegroundColor Yellow
    return $false
}

# اگر پارامتر داده نشده، راهنما نمایش بده
if (-not $Service -or -not $Token) {
    Write-Host @"

🔑 راهنمای استفاده:
════════════════════════════════════════════════════

استفاده:
    .\setup_token.ps1 -Service <نام_سرویس> -Token <توکن>

مثال‌ها:
    .\setup_token.ps1 -Service GitHub -Token "ghp_xxxxx"
    .\setup_token.ps1 -Service Google -Token "AIzaSy_xxxxx"
    .\setup_token.ps1 -Service HuggingFace -Token "hf_xxxxx"
    .\setup_token.ps1 -Service OpenAI -Token "sk-proj-xxxxx"
    .\setup_token.ps1 -Service Anthropic -Token "sk-ant-xxxxx"

سرویس‌های موجود:
    - GitHub        → GitHub Models API
    - Google        → Google Gemini API
    - HuggingFace   → Hugging Face API
    - OpenAI        → OpenAI GPT API
    - Anthropic     → Anthropic Claude API

نکته: بعد از تنظیم، Terminal را ببندید و دوباره باز کنید.

"@ -ForegroundColor Cyan
    exit 0
}

# تنظیم توکن بر اساس سرویس
switch ($Service) {
    "GitHub" {
        Set-APIToken -ServiceName "GitHub Models" -EnvVarName "GITHUB_TOKEN" -TokenValue $Token
        Start-Sleep -Seconds 1
        Test-APIToken -ServiceName "GitHub"
    }
    
    "Google" {
        Set-APIToken -ServiceName "Google Gemini" -EnvVarName "GOOGLE_API_KEY" -TokenValue $Token
        Start-Sleep -Seconds 1
        Test-APIToken -ServiceName "Google"
    }
    
    "HuggingFace" {
        Set-APIToken -ServiceName "Hugging Face" -EnvVarName "HUGGINGFACE_TOKEN" -TokenValue $Token
        Start-Sleep -Seconds 1
        Test-APIToken -ServiceName "HuggingFace"
    }
    
    "OpenAI" {
        Set-APIToken -ServiceName "OpenAI" -EnvVarName "OPENAI_API_KEY" -TokenValue $Token
        Start-Sleep -Seconds 1
        Test-APIToken -ServiceName "OpenAI"
    }
    
    "Anthropic" {
        Set-APIToken -ServiceName "Anthropic Claude" -EnvVarName "ANTHROPIC_API_KEY" -TokenValue $Token
        Start-Sleep -Seconds 1
        Test-APIToken -ServiceName "Anthropic"
    }
    
    default {
        Write-Host "❌ سرویس نامعتبر: $Service" -ForegroundColor Red
        Write-Host "سرویس‌های معتبر: GitHub, Google, HuggingFace, OpenAI, Anthropic" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n📊 وضعیت توکن‌ها:" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════" -ForegroundColor DarkGray

$tokens = @{
    "GitHub Models" = $env:GITHUB_TOKEN
    "Google Gemini" = $env:GOOGLE_API_KEY
    "Hugging Face" = $env:HUGGINGFACE_TOKEN
    "OpenAI" = $env:OPENAI_API_KEY
    "Anthropic" = $env:ANTHROPIC_API_KEY
}

foreach ($key in $tokens.Keys) {
    if ($tokens[$key]) {
        $preview = $tokens[$key].Substring(0, [Math]::Min(15, $tokens[$key].Length))
        Write-Host "✅ $key : $preview..." -ForegroundColor Green
    } else {
        Write-Host "❌ $key : تنظیم نشده" -ForegroundColor DarkGray
    }
}

Write-Host "`n💡 نکته: برای اعمال تغییرات، Terminal را ببندید و دوباره باز کنید." -ForegroundColor Yellow

Write-Host "`n🧪 برای تست تمام مدل‌ها اجرا کنید:" -ForegroundColor Cyan
Write-Host "    python test_ai_models.py" -ForegroundColor White

Write-Host "`n✅ تنظیم با موفقیت انجام شد!" -ForegroundColor Green
