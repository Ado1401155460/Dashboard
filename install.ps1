# 安装依赖脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  量化交易分析仪表盘 - 依赖安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

## 安装后端依赖
Write-Host "`n[1/2] 正在安装后端依赖..." -ForegroundColor Green
Set-Location -Path "C:\Users\Administrator\Desktop\Dashboard\backend"
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 后端依赖安装成功！" -ForegroundColor Green
} else {
    Write-Host "✗ 后端依赖安装失败！" -ForegroundColor Red
    exit 1
}

## 安装前端依赖
Write-Host "`n[2/2] 正在安装前端依赖..." -ForegroundColor Green
Set-Location -Path "C:\Users\Administrator\Desktop\Dashboard\frontend"
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 前端依赖安装成功！" -ForegroundColor Green
} else {
    Write-Host "✗ 前端依赖安装失败！" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  所有依赖安装完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n运行 .\start.ps1 启动服务" -ForegroundColor Yellow

