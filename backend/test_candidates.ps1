# Corrected PowerShell Commands for Testing

# Set headers
$headers = @{
    'Content-Type' = 'application/json'
}

# Test 1: Create candidate with array skills (recommended format)
Write-Host "🚀 Testing with array skills format..." -ForegroundColor Green

$body1 = @{
    name = 'David Kim'
    email = 'david.kim.array@example.com'
    position = 'DevOps Engineer'
    skills = @('Docker', 'Kubernetes', 'AWS', 'Jenkins')  # Array format
    experience_years = 4
    education = 'Computer Science'
    current_title = 'DevOps Specialist'
    resume_text = 'Experienced DevOps Engineer'
    resume_summary = 'Testing automation with array skills'
    interview_datetime = '2025-08-15T10:50:00'
} | ConvertTo-Json -Depth 10

try {
    $response1 = Invoke-RestMethod -Uri 'http://localhost:8000/api/candidates/' -Method POST -Headers $headers -Body $body1
    Write-Host "✅ Array format test passed!" -ForegroundColor Green
    Write-Host "📋 Response: $($response1 | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Array format test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Create candidate with string skills (fallback format)
Write-Host "`n🚀 Testing with string skills format..." -ForegroundColor Yellow

$body2 = @{
    name = 'Jane Smith'
    email = 'jane.smith.string@example.com'
    position = 'Software Engineer'
    skills = 'Python, Django, PostgreSQL, Redis'  # String format
    experience_years = 3
    education = 'Computer Engineering'
    current_title = 'Backend Developer'
    resume_text = 'Experienced Backend Developer'
    resume_summary = 'Testing automation with string skills'
    interview_datetime = '2025-08-16T14:30:00'
} | ConvertTo-Json -Depth 10

try {
    $response2 = Invoke-RestMethod -Uri 'http://localhost:8000/api/candidates/' -Method POST -Headers $headers -Body $body2
    Write-Host "✅ String format test passed!" -ForegroundColor Green
    Write-Host "📋 Response: $($response2 | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ String format test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Testing completed!" -ForegroundColor Magenta
