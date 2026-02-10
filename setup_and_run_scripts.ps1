@echo off
REM Set PowerShell execution policy to RemoteSigned for the current user
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"

REM Define the paths to your Python scripts
set "script1=C:\Users\Priyam\Desktop\python\Final\script1.py"
set "script2=C:\Users\Priyam\Desktop\python\Final\script2.py"
set "script3=C:\Users\Priyam\Desktop\python\Final\script3.py"
set "script4=C:\Users\Priyam\Desktop\python\Final\script4.py"

REM Start a new PowerShell terminal for each script
start powershell -NoExit -Command "& python '%script1%'"
start powershell -NoExit -Command "& python '%script2%'"
start powershell -NoExit -Command "& python '%script3%'"
start powershell -NoExit -Command "& python '%script4%'"

REM Optionally, display a message confirming the execution
echo Execution policy set to RemoteSigned and scripts are running.
