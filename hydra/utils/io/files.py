import json
import os
from logging import Logger, getLogger
from zipfile import ZipFile
from io import BytesIO


from .hash import generate_hash_from_bytes

def read_json(file, path=None):
    if path:
        file = os.path.join(path, file)
    with open(file) as f:
        return json.load(f)


def generate_file_hash(file_content: bytes) -> str:
    return generate_hash_from_bytes(file_content)

def extract_text_file(
            zip_content:bytes,
            base_path:str,
            file_name:str,
            file_format:str='.csv',
            logger:Logger=getLogger()
            ) -> list[str]:
        logger.info('Lendo o conteúdo do arquivo')
        zip_file = ZipFile(BytesIO(zip_content))
        csv_file_path = f'{base_path}{file_name}{file_format}'

        logger.info(f'Abrindo o csv {csv_file_path}')
        csv_file = zip_file.open(csv_file_path, 'r')
        csv_string = [line.decode('latin1').strip()
                      for line in csv_file.readlines()]
        logger.info(f'Arquivo {csv_file_path} lido')

        return csv_string
