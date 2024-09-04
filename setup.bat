@echo off

:: Crea un entorno virtual
python -m venv env

:: Activa el entorno virtual
call env\Scripts\activate

:: Cambia el directorio a la carpeta que contiene manage.py
cd C:\Projects\IS2_Django\IS2_Django\myproject

:: Instala las dependencias
pip install --upgrade pip
pip install -r requirements.txt

:: Ejecuta las migraciones
python manage.py migrate

:: Inicia el servidor de desarrollo
python manage.py runserver

:: Mantén la ventana abierta al finalizar
pause
