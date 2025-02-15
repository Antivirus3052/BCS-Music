@echo off
echo Updating GitHub repository...

REM Check if .git directory exists
IF NOT EXIST ".git" (
    echo Initializing new Git repository...
    git init
    
    REM Add remote
    git remote add origin https://github.com/Antivirus3052/BCS-Music.git
) ELSE (
    echo Git repository already exists. Updating...
)

REM Update .gitignore if needed
IF NOT EXIST ".gitignore" (
    echo Creating .gitignore...
    echo .env>.gitignore
    echo __pycache__/>>.gitignore
    echo *.pyc>>.gitignore
    echo venv/>>.gitignore
)

REM Remove Git LFS tracking
echo Removing Git LFS tracking...
IF EXIST ".gitattributes" del .gitattributes
git lfs uninstall

REM Stage changes
echo Staging changes...
git add .
git add bin/* -f

REM Commit changes
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg="Updated Discord Music Bot"
git commit -m "%commit_msg%"

REM Push changes
echo Pushing to GitHub...
git branch -M main
git push -u origin main -f

echo.
if errorlevel 1 (
    echo Failed to push changes. Please check your Git configuration and try again.
) else (
    echo Repository successfully updated!
)

pause