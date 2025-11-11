import pathlib
from urllib.parse import urlparse
from openai.types import FileObject


def is_valid_url(url: str) -> bool:
    try:
        url = str(url)
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_valid_path(path: str | pathlib.Path) -> bool:
    if isinstance(path, str):
        path = pathlib.Path(path)
    return path.exists()

def is_file_id(file: FileObject) -> bool:
    if isinstance(file, FileObject) and file.id:
        return True
    return False

