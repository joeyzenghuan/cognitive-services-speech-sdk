# Azure Speech Pronunciation Assessment - PowerShell Script
# Usage: .\pronunciation_assessment.ps1 -AudioFile "audio.wav" -ReferenceText "手机号码" -Language "zh-CN"

param(
    [Parameter(Mandatory=$true)]
    [string]$AudioFile,
    
    [Parameter(Mandatory=$true)]
    [string]$ReferenceText,
    
    [Parameter(Mandatory=$false)]
    [string]$Language = "zh-CN",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionKey = "YourSubscriptionKey",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "westus"
)

# Try loading .env if key/region were not provided or are placeholders
function Load-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return @{} }
    $envMap = @{}
    Get-Content -Raw -Path $Path | ForEach-Object { $_ -split "`n" } | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) { return }
        $idx = $line.IndexOf('=')
        if ($idx -gt 0) {
            $k = $line.Substring(0, $idx).Trim()
            $v = $line.Substring($idx+1).Trim().Trim('"')
            $envMap[$k] = $v
        }
    }
    return $envMap
}

if (($SubscriptionKey -eq "YourSubscriptionKey") -or [string]::IsNullOrWhiteSpace($Region)) {
    $dotenvPath = Join-Path -Path (Get-Location) -ChildPath ".env"
    $dotenv = Load-DotEnv -Path $dotenvPath
    if ($dotenv.ContainsKey('SPEECH_SUBSCRIPTION_KEY') -and $SubscriptionKey -eq "YourSubscriptionKey") {
        $SubscriptionKey = $dotenv['SPEECH_SUBSCRIPTION_KEY']
    }
    if ($dotenv.ContainsKey('SPEECH_REGION') -and [string]::IsNullOrWhiteSpace($Region)) {
        $Region = $dotenv['SPEECH_REGION']
    }
}

# Check if audio file exists
if (-not (Test-Path $AudioFile)) {
    Write-Error "Audio file '$AudioFile' not found"
    exit 1
}

# Build pronunciation assessment parameters
$pronParams = @{
    GradingSystem = "HundredMark"
    Granularity = "Phoneme"
    Dimension = "Comprehensive"
    ReferenceText = $ReferenceText
    EnableMiscue = $true
    EnableProsodyAssessment = $true
    PhonemeAlphabet = "IPA"
    NBestPhonemeCount = 5
} | ConvertTo-Json -Compress

# Base64 encode
$pronParamsBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($pronParams))

# Generate connection ID
$connectionId = (New-Guid).ToString("N")

# Build URL
$url = "https://$Region.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?format=detailed&language=$Language"

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Pronunciation Assessment Request" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Audio File: $AudioFile"
Write-Host "Reference Text: $ReferenceText"
Write-Host "Language: $Language"
Write-Host "Region: $Region"
Write-Host "Connection ID: $connectionId"
Write-Host ""
Write-Host "Sending request..." -ForegroundColor Yellow
Write-Host ""

# Read audio file as bytes
$audioBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $AudioFile))

# Prepare headers (Content-Type passed via -ContentType to avoid validation issues)
$headers = @{
    "Ocp-Apim-Subscription-Key" = $SubscriptionKey
    "Accept" = "application/json"
    "Connection" = "Keep-Alive"
    "Pronunciation-Assessment" = $pronParamsBase64
    "X-ConnectionId" = $connectionId
}

try {
    # Send request with explicit Content-Type
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $audioBytes -ContentType 'audio/wav'
    
    Write-Host "===================================" -ForegroundColor Green
    Write-Host "Response (Success)" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green
    
    # Pretty print JSON
    $response | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host "===================================" -ForegroundColor Red
    Write-Host "Error" -ForegroundColor Red
    Write-Host "===================================" -ForegroundColor Red
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
        Write-Host ("Status Code: {0}" -f $_.Exception.Response.StatusCode.value__) -ForegroundColor Red
    }
    Write-Host ("Error Message: {0}" -f $_.Exception.Message) -ForegroundColor Yellow

    # Try to print response body
    try {
        $resp = $_.Exception.Response
        if ($resp -and $resp.Content) {
            $body = $resp.Content.ReadAsStringAsync().Result
            if ($body) {
                Write-Host "Response Body:" -ForegroundColor Yellow
                Write-Host $body
            }
        } elseif ($_.ErrorDetails -and $_.ErrorDetails.Message) {
            Write-Host "Error Details:" -ForegroundColor Yellow
            Write-Host $_.ErrorDetails.Message
        }
    } catch {}

    exit 1
}
