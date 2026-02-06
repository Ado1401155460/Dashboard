# 快速启动脚本

## 启动后端
Write-Host "正在启动后端服务..." -ForegroundColor Green
Set-Location -Path "C:\Users\Administrator\Desktop\Dashboard\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

## 启动前端
Write-Host "正在启动前端服务..." -ForegroundColor Green
Set-Location -Path "C:\Users\Administrator\Desktop\Dashboard\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host "`n服务启动完成！" -ForegroundColor Cyan
Write-Host "后端 API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "前端界面: http://localhost:3000" -ForegroundColor Yellow

