Hay que utilizar el entorno virtual .venv para que las dependencias que instalemos con requirements.txt no se queden en el pc 
y sólo se utilicen en este proyecto, para no entorpecer futuros proyectos.

1-Para activar Entorno virtual:
.venv\Scripts\Activate.ps1

2-Instalar Dependencias:
pip install -r requirements.txt

3-Iniciar proyecto:
streamlit run app.py