rmdir dist /s /q
rmdir build /s /q
pyinstaller ..\src\install.py
copy dist\install\*.* . /Y
pause