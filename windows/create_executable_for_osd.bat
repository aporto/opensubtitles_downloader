rmdir dist /s /q
rmdir build /s /q
pyinstaller ..\src\osd.py
copy dist\osd\*.* . /Y
pause