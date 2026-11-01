@echo off
title Indian Sign Language (ISL) Translator
echo ======================================================================
echo    INDIAN SIGN LANGUAGE (ISL) TRANSLATOR - CAMERA TO TEXT AND VOICE
echo ======================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [Setup] Creating Python virtual environment...
    py -3.12 -m venv venv
    echo [Setup] Installing dependencies...
    venv\Scripts\pip install opencv-python "mediapipe<=0.10.14" "numpy<2" scikit-learn flask pyttsx3 pillow pymongo
)

echo [Launch] Starting Web Application...
start "" http://127.0.0.1:5000
venv\Scripts\python.exe app.py

pause

