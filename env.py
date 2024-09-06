import os
from fastapi import HTTPException


def secrets(value: str) -> str:
    """
    Función para obtener los secrets, en este caso se obtienen
    del archivo .bashrc que funciona como nuestro .env

    Parameters:
        value -> str

    Output:
        secret -> str
    """
    try:
        secret = os.getenv(value)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=ex)
    return str(secret)
