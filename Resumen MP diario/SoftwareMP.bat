@echo off
REM Configurar el entorno virtual
echo Activando el entorno virtual de Python...
call C:\ResumenMP\venv\Scripts\activate.bat

REM Ir al directorio del archivo
cd C:\ResumenMP\softconsultaMP.py

REM Ejecutar el script Python
echo Ejecutando el script Python...
python softconsultaMP.py

REM Desactivar el entorno virtual (opcional)
deactivate

echo Proceso completado.
pause
