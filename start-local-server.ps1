# 本地 HTTP 预览：请用 http://127.0.0.1:8765/ ，勿用 file:// 打开含中文路径的 HTML
Set-Location -LiteralPath $PSScriptRoot
$port = 8765
Write-Host ""
Write-Host "  浏览器打开: http://127.0.0.1:$port/"
Write-Host "  保持本窗口运行，Ctrl+C 停止"
Write-Host ""
python -m http.server $port --bind 127.0.0.1
