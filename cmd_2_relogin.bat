@echo off
title 重新登录
color e2
echo.

if not (%1%)==() (
  set proxy=%1%
)

"C:/Program Files/Python311/python.exe" %~dp0/2.relogin.py %proxy%