
import { criarClienteHttp } from './cliente'
import { configuracao, type ConfiguracaoApi } from './configuracao'
import { ErroApi } from './erros'
import { obterTokenAcesso } from './sessao'

export interface Documento {
  documento_id: string
  titulo: string
  formato_origem: string
  nivel_documento_estimado: string | null
  dominio_conhecimento: string | null
  classificador_usado: string | null
  status_upload: string
  criado_em: string
}

interface RespostaHistoricoDocumentos {
  itens: Documento[]
  total: number
}

export function criarApiDocumentos(
  config: ConfiguracaoApi,
  obterToken = obterTokenAcesso,
  transporte: typeof fetch = fetch,
) {
  const requisitar = criarClienteHttp(config, obterToken, transporte)

  async function exigirResposta<T>(
    promessa: Promise<T | undefined>,
  ): Promise<T> {
    const resposta = await promessa

    if (!resposta) {
      throw new ErroApi('RESPOSTA_INVALIDA')
    }

    return resposta
  }

  return {
    async listar(signal?: AbortSignal): Promise<Documento[]> {
      if (config.usarMock) {
        return []
      }

      const resposta = await exigirResposta(
        requisitar<RespostaHistoricoDocumentos>('documentos', {
          method: 'GET',
          signal,
        }),
      )

      return resposta.itens
    },
  }
}

export const apiDocumentos = criarApiDocumentos(configuracao)
