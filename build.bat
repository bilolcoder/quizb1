@echo off
chcp 65001 >nul
title Iqtisodiy Tahlil — Vercel / Static Build

cd /d "%~dp0"
echo ======================================================
echo    VERCEL / STATIK HOSTING UCHUN BUNDLE YARATISH
echo ======================================================
echo.

npm run build

echo.
echo ======================================================
echo [MUVAFFAQIYAT] dist/ papkasiga statik fayllar tayyorlandi!
echo Ushbu dist/ papkasini Vercel yoki Netlify ga joylashtirishingiz mumkin.
echo ======================================================
pause

