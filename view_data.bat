@echo off
echo ========================================
echo   EXPOSYS DATABASE VIEWER
echo ========================================
echo.

set MYSQL="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

echo --- STUDENTS ---
%MYSQL% -u root -proot exposys_db -e "SELECT id, name, email, branch, internship_domain, duration, created_at FROM students;" 2>nul

echo.
echo --- PAYMENTS ---
%MYSQL% -u root -proot exposys_db -e "SELECT p.id, s.name, p.transaction_id, p.amount, p.status, p.created_at FROM payments p JOIN students s ON p.student_id=s.id;" 2>nul

echo.
echo --- CONTACTS ---
%MYSQL% -u root -proot exposys_db -e "SELECT id, name, email, subject, created_at FROM contacts;" 2>nul

echo.
echo --- ADMINS ---
%MYSQL% -u root -proot exposys_db -e "SELECT id, name, email, created_at FROM admins;" 2>nul

echo.
pause
