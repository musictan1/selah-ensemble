# Fix Git Pager Issue in PowerShell
Write-Host "Fixing Git pager issue in PowerShell..." -ForegroundColor Green

# Set environment variables
$env:GIT_PAGER = "cat"
$env:LESS = "-F"

# Set Git config globally
Write-Host "Setting Git config globally..." -ForegroundColor Yellow
git config --global core.pager cat
git config --global gui.pager cat
git config --global help.pager cat

# Set Git config locally
Write-Host "Setting Git config locally..." -ForegroundColor Yellow
git config core.pager cat
git config gui.pager cat
git config help.pager cat

Write-Host "Git pager should be fixed now!" -ForegroundColor Green
Write-Host "Test with: git status" -ForegroundColor Cyan
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")










