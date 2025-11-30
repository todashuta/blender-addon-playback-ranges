@echo off

pushd %~dp0

if "%1" == "" (
	echo Usage:
	echo   make.bat build
	echo   make.bat validate
	echo   make.bat validate add-on-package.zip
	goto EOF
)

set "BLENDER_EXE=blender-4.2.exe"
where /q "%BLENDER_EXE%"
if errorlevel 1 (
	echo %BLENDER_EXE% not found!
	goto ERR
)

:argv_loop
if NOT "%1" == "" (
	if "%1" == "build" (
		"%BLENDER_EXE%" --command extension build
		if errorlevel 0 (
			goto EOF
		) else (
			goto ERR
		)
	) else if "%1" == "validate" (
		"%BLENDER_EXE%" --command extension validate %2
		if errorlevel 0 (
			goto EOF
		) else (
			goto ERR
		)
	)

	shift /1
	goto argv_loop
)

:EOF
exit /b 0
:ERR
exit /b 1
