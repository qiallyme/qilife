# Step 1: Optional – Remove old venv if needed
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
    Write-Host "🧹 Old virtual environment deleted."
}

# Step 2: Create new venv using Python 3.11
$pythonPath = "C:\Users\codyr\AppData\Local\Programs\Python\Python311\python.exe"
& $pythonPath -m venv .venv
Write-Host "✅ New virtual environment created using Python 3.11."

# Step 3: Install requirements directly using pip
$pipPath = ".\.venv\Scripts\pip.exe"
if (Test-Path $pipPath) {
    if (Test-Path "requirements.lock.txt") {
        Write-Host "📦 Installing from requirements.lock.txt..."
        & $pipPath install -r "requirements.lock.txt"
    } elseif (Test-Path "requirements.txt") {
        Write-Host "📦 Installing from requirements.txt..."
        & $pipPath install -r "requirements.txt"
    } else {
        Write-Host "⚠️ No requirements file found."
    }
} else {
    Write-Host "❌ pip not found. Check your virtual environment."
}