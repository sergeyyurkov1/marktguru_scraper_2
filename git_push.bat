@echo off
cls

@REM call .\venv\Scripts\activate

call rmdir /s /q .git

echo init
call git init
echo git remote add origin
call git remote add origin https://github.com/sergeyyurkov1/marktguru_scraper_2.git
echo git add
call git add *

echo git commit
call git commit --all --message="commit"

echo git push
call git push --force origin main

pause
