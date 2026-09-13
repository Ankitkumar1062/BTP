@echo off
echo ===============================================================================
echo Running Tsetlin Machine - MLIR - CPOG Complete Pipeline...
echo ===============================================================================
if exist "C:\Users\ankit\python_embed\python.exe" (
    "C:\Users\ankit\python_embed\python.exe" run_full_pipeline.py
) else (
    python run_full_pipeline.py
)
pause
