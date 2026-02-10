@echo off
REM Set PowerShell execution policy to RemoteSigned for the current user
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"

REM Define the base directory and log directory using environment variables
set "baseDir=%~dp0"  REM The directory where this batch file is located
set "logDir=%baseDir%log"
set "dataDir=%baseDir%data"
set "importDir=%dataDir%\import"
set "outputDir=%dataDir%\output"
set "combineDir=%dataDir%\combine"
set "playerstsDir=%dataDir%\playersts"
set "ssDir=%dataDir%\ss"
set "xlsx_filesDir=%dataDir%\xlsx_files"

REM Create the log directory if it does not exist
if not exist "%logDir%" mkdir "%logDir%"

REM Define the paths to your executable and Python scripts relative to the base directory
set "script1=%baseDir%finalv6.py"
set "script2=%baseDir%finalv2v2.py"
set "script3=%baseDir%combine.py"
set "script4=%baseDir%json_clean.py"
set "script5=%baseDir%homevsawayfix.py"
set "script6=%baseDir%sofaratteam.py"
set "script7=%baseDir%Call.py"
set "script8=%baseDir%cleaning.py"
set "script9=%baseDir%format_cs_v2.py"
set "script10=%baseDir%last_clear_before_import.py"
set "script11=%baseDir%gs_sheet.py"
set "script12=%baseDir%playerssts.py"
set "script13=%baseDir%ply_sts_cl.py"
set "script14=%baseDir%last_play.py"
set "script15=%baseDir%play_sf_fetch.py"
set "script16=%baseDir%rating_playr.py"
set "script17=%baseDir%gs_ply_sts.py"

REM Remove any previous marker file created by finalv6.py
if exist "%baseDir%finalv6_done.txt" del /Q "%baseDir%finalv6_done.txt"

REM Run finalv6.py in the background and wait for "ook boss" signal
start python "%script1%"

REM Wait until the finalv6_done.txt file is created, indicating "ook boss" is printed
echo Waiting for "ook boss" signal...
:waitLoop
if not exist "%baseDir%finalv6_done.txt" (
    timeout /T 1 >nul
    goto waitLoop
)

REM Kill the Python process running finalv6.py once the signal is detected
echo "ook boss" detected. Killing finalv6.py...
taskkill /IM python.exe /F

REM Proceed with running the remaining scripts
start /wait powershell -NoExit -Command "& python '%script2%' > '%logDir%\finalv2v2.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script3%' > '%logDir%\combine.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script4%' > '%logDir%\json_clean.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script5%' > '%logDir%\homevsawayfix.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script6%' > '%logDir%\sofaratteam.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script7%' > '%logDir%\Call.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script8%' > '%logDir%\cleaning.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script9%' > '%logDir%\format_cs_v2.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script10%' > '%logDir%\last_clear_before_import.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script11%' > '%logDir%\gs_sheet.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script12%' > '%logDir%\playerssts.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script13%' > '%logDir%\ply_sts_cl.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script14%' > '%logDir%\last_play.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script15%' > '%logDir%\play_sf_fetch.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script16%' > '%logDir%\rating_playr.log' 2>&1; exit"
start /wait powershell -NoExit -Command "& python '%script17%' > '%logDir%\gs_ply_sts.log' 2>&1; exit"

REM Move files from the data folder to a new directory named with the current date
set "currentDate=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%"
set "dateDir=%dataDir%\%currentDate%"
if not exist "%dateDir%" mkdir "%dateDir%"
if exist "%dataDir%\*" move "%dataDir%\*" "%dateDir%"

REM Ensure all processes are completed before deleting files
REM Delete files in the import directory
if exist "%importDir%\*" del /Q "%importDir%\*"

REM Ensure all processes are completed before deleting files
REM Delete files in the output directory
if exist "%outputDir%\*" del /Q "%outputDir%\*"

REM Ensure all processes are completed before deleting files
REM Delete files in the SS directory
if exist "%ssDir%\*" del /Q "%ssDir%\*"

REM Ensure all processes are completed before deleting files
REM Delete files in the output directory
if exist "%xlsx_filesDir%\*" del /Q "%xlsx_filesDir%\*"

REM Move files in the combine directory to the playersts directory after all scripts have run
if not exist "%playerstsDir%" mkdir "%playerstsDir%"
if exist "%combineDir%\*" move "%combineDir%\*" "%playerstsDir%"

REM Display a message and countdown before closing all terminals
echo All processes are done. Closing all terminals in 10 seconds...
for /L %%i in (10,-1,1) do (
    echo Closing in %%i seconds...
    timeout /T 1 /NOBREAK >nul
)

REM Close all terminals
exit
