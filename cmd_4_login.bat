@echo off
title 登录账号
@REM color e2
echo.

if not (%1%)==() (
  set email=%1%
)
if not (%2%)==() (
  set proxy=%2%
)

"C:/Program Files/Python311/python.exe" %~dp0/4.login_email.py %email% %proxy%