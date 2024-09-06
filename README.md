# Proyecto OCR con FastAPI

1. Instalación de librerias y configuracion de ambiente virtual

- Linux/Mac: python3 -m venv myenv (Cambia myenv por el nombre tu ambiente virtual)

- Windows: py -m venv myenv (Cambia myenv por el nombre tu ambiente virtual)

2. Crea y activa tu ambiente virtual

- Linux/Mac: source myenv/bin/activate
- Windows: myenv\Scripts\activate

3. Instala los requerimientos

Para poder correr el proyecto es necesario crear un ambiente virtual
e instalar los requerimientos que se encuentran en la carpeta requirements/
en el archivo base.txt, esto nos instalara todas las dependencias necesarias.

La manera más rapida de poder instalar las dependencias seria con el comando:

```
pip install -r requirements/base.txt
```

4. Agrega las variables de entorno, en este caso es necesario en .bashrc para
Linux y Mac o su correspondiente en Windows

Para Linux/Mac

# Edita el archivo .bashrc o .zshrc
nano ~/.bashrc

# Agrega las variables al final del archivo
export azure_url="valor_del_secret"
export azure_key="valor_del_secret"

# Recargar el archivo .bashrc para que las variables estén disponibles
source ~/.bashrc

Para el caso de Windows

# Usar el siguiente comando en PowerShell para establecer las variables
$env:azure_url="valor_del_secret"
$env:azure_key="valor_del_secret"

Una vez tenemos todo lo anterior es necesario iniciar el servidor
Para ello se debe de correr el siguiente comando

```
fastapi dev main.py
```

Con esto podemos mandar la request que se encuentra dentro de la coleccion
postman.


Coleccion de postman "WeeOcr.postman_collection.json"
Archivo de prueba "ine.pdf"
