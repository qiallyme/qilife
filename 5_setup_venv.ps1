# Step 1: Optional – Remove old venv if needed
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
    Write-Host "🧹 Old virtual environment deleted."
}

# Step 2: Create new venv with Python 3.11
& "C:\Users\codyr\AppData\Local\Programs\Python\Python311\python.exe" -m venv .venv
Write-Host "✅ New virtual environment created using Python 3.11."

# Step 3: Reminder to activate manually
Write-Host "`n⚠️  Run the following to activate it:"
Write-Host ".\.venv\Scripts\activate`n"

# Step 4: Install dependencies (once activated)
Write-Host "📦 After activating, run:"
Write-Host "pip install -r requirements.txt"
