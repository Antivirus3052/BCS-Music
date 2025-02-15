REM filepath: /C:/Users/Panther/Desktop/Music_BotVS/upload.bat
@echo off
echo Uploading project to GitHub repository...

REM Remove existing Git repository if exists
rd /s /q .git 2>nul

REM Initialize new Git repository
echo Initializing Git repository...
git init

REM Create/update .gitignore
echo Ensuring .gitignore is properly set...
echo .env>.gitignore
echo __pycache__/>>.gitignore
echo *.pyc>>.gitignore
echo venv/>>.gitignore

REM Configure Git LFS for large files
echo Configuring Git LFS...
git lfs install
git lfs track "*.exe"
git lfs track "*.dll"

REM Add all files except those in .gitignore
echo Adding files to staging...
git add .
git add ffmpeg/bin/* -f

REM Commit changes with default message
echo Committing changes...
git commit -m "Updated Discord Music Bot with FFmpeg binaries"

REM Add remote and push
echo Setting up remote repository...
git remote add origin https://github.com/Antivirus3052/BCS-Music.git
echo Pushing to GitHub...
git branch -M main
git push -u origin main -f

echo.
if errorlevel 1 (
    echo Failed to upload project. Please check your Git configuration and try again.
) else (
    echo Project successfully uploaded to GitHub!
)

pause