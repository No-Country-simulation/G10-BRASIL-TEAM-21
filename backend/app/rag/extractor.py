"""Extração de texto de arquivos enviados para ingestão."""

from io import BytesIO

import pdfplumber

class FormatoNaoSuportadoError(ValueError):
    """Indica que o arquivo enviado não é PDF nem TXT."""


def extrair_texto(conteudo: bytes, nome_arquivo: str) -> str:
    """Extrai texto de PDF ou TXT, preservando a ordem original do arquivo."""
    extensao = nome_arquivo.rsplit(".", maxsplit=1)[-1].lower() if "." in nome_arquivo else ""
    if extensao == "pdf":
        with pdfplumber.open(BytesIO(conteudo)) as pdf:
            return "\n".join(pagina.extract_text() or "" for pagina in pdf.pages).strip()
    if extensao == "txt":
        return conteudo.decode("utf-8-sig").strip()
    raise FormatoNaoSuportadoError("Formato não suportado. Envie um arquivo PDF ou TXT.")
