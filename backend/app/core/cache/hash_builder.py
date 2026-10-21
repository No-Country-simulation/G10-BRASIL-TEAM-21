import hashlib
import json

from ...ports.cache_key_builder import CacheKeyBuilder


class HashCacheKeyBuilder(CacheKeyBuilder):
    def build(
        self,
        hash_conteudo: str,
        perfil_destinatario: str,
        formato_saida: str,
        nicho_setor: str,
        nivel_detalhe: str,
        incluir_analogias: bool,
        incluir_microlearning: bool,
    ) -> str:
        parametros = {
            "formato_saida": formato_saida,
            "hash_conteudo": hash_conteudo,
            "incluir_analogias": incluir_analogias,
            "incluir_microlearning": incluir_microlearning,
            "nivel_detalhe": nivel_detalhe,
            "nicho_setor": nicho_setor,
            "perfil_destinatario": perfil_destinatario,
        }
        serializado = json.dumps(
            parametros,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(serializado.encode("utf-8")).hexdigest()
