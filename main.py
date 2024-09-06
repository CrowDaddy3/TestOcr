import json
import io
from fastapi import (FastAPI, File, UploadFile, HTTPException)
from pdf2image import convert_from_bytes
from fastapi.responses import JSONResponse
from utils import (
    client,
    search_fields,
    date_regex,
    get_ocr_results,
    sort_data
)

# Se crea una instancia de FastAPI para crear el API
app = FastAPI()


# Se le asigna un metodo en este caso post para poder
# recibir los documentos a extraer.
@app.post("/extract_pdf/")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Función para recibir los documentos en pdf que van a ser
    analizados y en los cuales se va a buscar información especifica.
    Esta función ocupa un cliente de Azure para poder mandar el documento
    y extraer la información.

    Parameters:
        file: UploadFile -> File (pdf)

    Output:
        json object
    """
    # Validamos que sea un archivo pdf
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="El archivo necesita ser un PDF")

    # leemos el contenido del pdf
    pdf_content = await file.read()

    try:
        # se convierte el pdf en imagenes
        images = convert_from_bytes(pdf_content)
        result_to_consult = []
        information = []

        # Itera sobre la lista de imágenes `images`,
        # obteniendo tanto el índice `i` como la imagen `image`.
        for i, image in enumerate(images):
            # Crea un buffer en memoria para almacenar datos binarios.
            buffered = io.BytesIO()
            # Guarda la imagen actual en el buffer, utilizando el formato PNG.
            # Esto convierte la imagen en un flujo de bytes en lugar
            # de guardarla en el disco.
            image.save(buffered, format="PNG")
            # Mueve el cursor del buffer al inicio.
            # Esto es necesario porque después de escribir
            # en el buffer, el cursor queda al final,
            # y debemos leer desde el principio.
            buffered.seek(0)

            # Envia el contenido del buffer (que contiene la imagen) al cliente
            # para leer la imagen directamente desde el flujo de bytes.
            # `client.read_in_stream` es un método que está leyendo o
            # procesando la imagen.
            result = client.read_in_stream(
                buffered,
                raw=True
            )

            # Buscamos el id de operacion con el cual podemos obtener los
            # resultados usando otro metodo del mismo cliente
            ocr_results = result.headers["Operation-Location"].split("/")[-1]
            result_to_consult.append(ocr_results)

        # En caso de mandar varias imagenes se itera sobre de estos valores
        # para obtener la información contenida en cada una de ellas
        for res in result_to_consult:
            # Se hace uso de la funcion get_ocr_results, la cual nos devolvera
            # una lista con los resultados de la extracción
            result = await get_ocr_results(res)
            information.append(result)
        page_number = 1
        ocr_data = []
        for info in information:
            # Para casos practicos solo se leera la información de la primer
            # hoja, para casos reales se necesita ajutstar el codigo
            if page_number > 1:
                break
            lines = info[0].lines
            page_number += 1
            for line in lines:
                # se crea una lista en la cual se guarda el texto junto
                # con las coordenadas de los vertices que componen
                # el recuadro compuesto por el ocr de Azure
                ocr_data.append([line.text, line.bounding_box])
        # Ordenamos la informacion con la funcion sort_data
        ordered_data = await sort_data(ocr_data)
        final_response = {}
        for i in range(len(ordered_data)):
            # Una vez ordenada la información procedemos a buscar las palabras
            # clave que van a ser las key de nuestro diccionario de salida
            # en este caso es información reelevante de una INE
            # para casos practicos y como software a la medida el codigo
            # esta destinado a un caso en particular, para casos generales
            # es necesario ajustar el codigo
            for value in search_fields:
                if value in ordered_data[i]:
                    if value == "NOMBRE":
                        for j in range(i, len(ordered_data)):
                            if ordered_data[j] == "DOMICILIO":
                                nombre = [
                                    value for value in ordered_data[i+1:j]]
                        final_response[value] = " ".join(nombre)
                    elif value == "FECHA DE NACIMIENTO":
                        for value_ in ordered_data:
                            if date_regex.match(value_):
                                final_response[value] = value_
                    elif value =="GENERO":
                        gender = ordered_data[i].split()[1]
                        final_response[value] = gender
                    elif value == "CURP":
                        curp = ordered_data[i].split()[1]
                        final_response[value] = curp
                    elif value == "CLAVE DE ELECTOR":
                        clave = ordered_data[i].split()[3]
                        final_response[value] = clave
                    elif value == "DOMICILIO":
                        for j in range(i, len(ordered_data)):
                            if "CLAVE" in ordered_data[j]:
                                direccion = [
                                    value for value in ordered_data[i+1:j]]
                        final_response[value] = " ".join(direccion)
        # Una vez terminado todo el proceso, retornamos el diccionario con
        # la informacion obtenida de la extraccion del OCR
        return JSONResponse(content={"data": final_response})

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
