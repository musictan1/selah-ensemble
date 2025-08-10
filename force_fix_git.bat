@echo off
echo Force fixing Git pager issue...
echo.

echo Setting environment variables...
set GIT_PAGER=cat
set LESS=-F
set GIT_CONFIG_PARAMETERS="core.pager=cat"
set GIT_CONFIG_GLOBAL="core.pager=cat"

echo.
echo Setting Git config globally...
git config --global core.pager cat
git config --global gui.pager cat
git config --global help.pager cat

echo.
echo Setting Git config locally...
git config core.pager cat
git config gui.pager cat
git config help.pager cat

echo.
echo Git pager should be completely disabled now!
echo Test with: git status
echo.
pause
