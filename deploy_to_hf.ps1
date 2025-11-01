# HuggingFace Deployment Script
# Run this in PowerShell after setting your HF token

# Replace <YOUR_HF_TOKEN> with your actual token from https://huggingface.co/settings/tokens

$HF_TOKEN = "<YOUR_HF_TOKEN>"  # Replace this!

# Configure git remote with credentials
git remote remove huggingface 2>$null
git remote add huggingface "https://Premkumar0709:$HF_TOKEN@huggingface.co/spaces/Premkumar0709/krishisutra-ai-powered-agricultural-intelligence"

# Push to HuggingFace
Write-Host "Pushing to HuggingFace Spaces..." -ForegroundColor Green
git push huggingface main --force

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "Visit your Space at:" -ForegroundColor Cyan
Write-Host "https://huggingface.co/spaces/Premkumar0709/krishisutra-ai-powered-agricultural-intelligence" -ForegroundColor Cyan
