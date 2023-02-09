@echo off
title 自动刷量
@REM color e2
echo.

if (%1%)!=() (
  set file=%1%
)

"C:/Program Files/Python311/python.exe" %~dp0/3.fast_lunch.py %file%