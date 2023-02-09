@echo off
title 登录账号
@REM color e2
echo.

if (%1%)==() (
  set email="cdcdx888@gmail.com"
) else (
  set email=%1%
)

"C:/Program Files/Python311/python.exe" %~dp0/4.login_email.py %email%