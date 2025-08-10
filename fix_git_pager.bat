@echo off
echo Fixing Git pager issue...
set GIT_PAGER=cat
set LESS=-F
set GIT_CONFIG_PARAMETERS="core.pager=cat"
echo Git pager fixed! Now Git commands should work without pausing.
pause
