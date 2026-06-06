@echo off
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -proot -e "CREATE DATABASE IF NOT EXISTS exposys_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo Database created successfully!
