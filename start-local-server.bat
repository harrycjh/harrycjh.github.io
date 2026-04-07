@echo off
REM 本地预览：请用下面这个纯英文地址访问，不要从资源管理器拖 index.html 到浏览器（file:// + 中文路径易失败）
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  在浏览器地址栏输入或复制:
echo    http://127.0.0.1:8765/
echo  本窗口需保持打开；停止服务请按 Ctrl+C
echo.
py -3 -m http.server 8765 --bind 127.0.0.1 2>nul
if errorlevel 1 python -m http.server 8765 --bind 127.0.0.1
pause
