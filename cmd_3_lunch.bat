@echo off
title 自动刷量
@REM color e2
echo.

if not (%1%)==() (
  set file=%1%
)
if not (%2%)==() (
  set proxy=%2%
)

"C:/Program Files/Python311/python.exe" %~dp0/3.fast_lunch.py %file% %proxy%