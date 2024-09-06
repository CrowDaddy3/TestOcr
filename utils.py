import asyncio
import re
from typing_extensions import List, Any
from env import secrets
from fastapi import HTTPException
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# Obtencion de secrets
KEY = secrets("azure_key")
URL = secrets("azure_url")

# Se crea una instancia de cliente con la clase ComputerVisualClient de Azure
client = ComputerVisionClient(URL, CognitiveServicesCredentials(KEY))

# Se definen los campos a buscar para su return
search_fields = [
    "NOMBRE",
    "FECHA DE NACIMIENTO",
    "GENERO",
    "CURP",
    "CLAVE DE ELECTOR",
    "DOMICILIO",
]

# Se define un regex para encontrar la fecha de nacimiento en la
# información extraida por el OCR
regex_dob = r'^([0-2][0-9]|3[0-1])/(0[1-9]|1[0-2])/([0-9]{4})$'
date_regex = re.compile(regex_dob)


async def get_ocr_results(operation_id: str) -> List[Any]:
    """
    Función para obtener los resultados de la extración realizada
    por el OCR de azure.
    Se utiliza el metodo "get_read_result" de la instancia client
    creada fuera de la función.

    Esta función requiere de un operation_id que es proporcionado
    por azure al momento de utilizar el metodo read_in_stream,
    al consultar el resultado y obtener un status exitoso
    la funcion retorna la lista de los resultados obtenidos al
    momento de la extraccion.

    Parameters:
        operation_id -> str

    Output:
        result -> List[Any]
    """
    timeout = 60
    star_time = asyncio.get_event_loop().time()

    while True:
        result = client.get_read_result(operation_id)
        if result.status == "succeeded":
            return result.analyze_result.read_results
        elif result.status == "failed":
            raise HTTPException(status_code=500, detail="Proceso Fallido")

        elapsed_time = asyncio.get_event_loop().time() - star_time
        if elapsed_time > timeout:
            raise HTTPException(
                status_code=408,
                detail="Tiempo de ejecucion excedido"
            )


async def sort_data(ocr_data: List[List[str] | List[float]]) -> Any:

    """
    Función para ordenar la información que ha sido filtrada
    dentro de los resultados obtenidos por el ocr, la manera
    de ordenar es sumandando las coordenadas del primer vertice
    para ordenarlos de manera que se pueda filtrar más facilmente
    la información que se va a buscar.

    Pameters:
        ocr_data -> List[List[str]] | List[Float]

    Output:
        ocr_data_ -> [Any]
    """

    ocr_data = sorted(ocr_data, key=lambda x: (x[1][0] + x[1][1]))
    ocr_data_ = [value[0] for value in ocr_data]

    return ocr_data_
