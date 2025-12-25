# PowerShell script to run both frontend and backend servers
# This script starts both the Docusaurus frontend and the RAG backend

Write-Host "Starting Digital Book Application..." -ForegroundColor Green

# Function to start the backend
function Start-Backend {
    Write-Host "Starting RAG backend server..." -ForegroundColor Yellow

    # Change to the rag-backend directory
    Set-Location -Path ".\rag-backend"

    # Start the backend server using Python
    $backendProcess = Start-Process -FilePath "python" -ArgumentList "run-backend.py" -PassThru -NoNewWindow

    Write-Host "Backend server started with PID: $($backendProcess.Id)" -ForegroundColor Green

    # Return to the main directory
    Set-Location -Path ".."

    return $backendProcess
}

# Start the backend server
$backendProcess = Start-Backend

# Wait a moment for the backend to start
Start-Sleep -Seconds 3

# Start the frontend server
Write-Host "Starting Docusaurus frontend server..." -ForegroundColor Yellow
npm start

# If we get here (frontend stopped), also stop the backend
if ($backendProcess -and !$backendProcess.HasExited) {
    Write-Host "Stopping backend server..." -ForegroundColor Yellow
    Stop-Process -Name "python" -ErrorAction SilentlyContinue
}