@echo off
chcp 65001 >nul
title Iqtisodiy Tahlil — Web Platforma

cd /d "%~dp0"
echo ======================================================
echo    IQTISODIY TAHLIL — WEB TEST PLATFORMASI
echo ======================================================
echo.
echo [*] Mahalliy server ishga tushirilmoqda...
echo [*] Brauzeringizda quyidagi manzil ochiladi: http://localhost:3000
echo.

start http://localhost:3000
npm run dev
pause

