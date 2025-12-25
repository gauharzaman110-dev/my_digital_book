# PowerShell script to run only the backend server
# This script starts just the RAG backend server

Write-Host "Starting RAG Backend Server for Digital Book Application..." -ForegroundColor Green

# Change to the rag-backend directory
Set-Location -Path ".\rag-backend"

Write-Host "Environment: $(Get-Location)" -ForegroundColor Cyan

# Start the backend server using Python
Write-Host "Starting backend server..." -ForegroundColor Yellow
python run-backend.py

Write-Host "Backend server stopped." -ForegroundColor Green