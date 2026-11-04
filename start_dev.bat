@echo off
chcp 65001 >nul
title Iqtisodiy Tahlil — Web Platforma (Dev Server)

cd /d "%~dp0"
echo ======================================================
echo    IQTISODIY TAHLIL — DEVELOPMENT SERVER
echo ======================================================
echo.
echo [*] Mahalliy Vite serveri ishga tushirilmoqda...
echo [*] Brauzer manzili: http://localhost:3000
echo.

start http://localhost:3000
call npm run dev

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [XATOLIK] Server to'xtatildi yoki xatolik yuz berdi.
)

echo.
echo Server to'xtatildi. Terminal yopilishi uchun istalgan tugmani bosing...
pause

