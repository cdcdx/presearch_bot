@echo off
title 注册账号
color e2
echo.

if not (%1%)==() (
  set proxy=%1%
)

"C:/Program Files/Python311/python.exe" %~dp0/1.reg_presearch.py %proxy%