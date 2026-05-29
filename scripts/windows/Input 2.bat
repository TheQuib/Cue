@echo off
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0_cue.ps1" -Command "input_hdmi2"
pause
