@ECHO off

set "script_path=%~dp0"
set "script_path=%script_path%Start.py"

python %script_path% %*