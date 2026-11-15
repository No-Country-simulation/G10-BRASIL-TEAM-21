import { criarClienteHttp } from './cliente'
import { configuracao, type ConfiguracaoApi } from './configuracao'
import { ErroApi } from './erros'
import { obterTokenAcesso } from './sessao'
import type {
  RespostasTesteRequest,
  RespostasTesteResponse,
  TesteNivelResponse,
} from './tipos'

export function criarApiTestes(
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
    async iniciar(): Promise<TesteNivelResponse> {
      if (config.usarMock) {
        throw new ErroApi('NAO_IMPLEMENTADO', 501)
      }

      return exigirResposta(
        requisitar<TesteNivelResponse>('testes-nivel', {
          method: 'POST',
        }),
      )
    },

    async responder(
      testeId: string,
      payload: RespostasTesteRequest,
    ): Promise<RespostasTesteResponse> {
      if (config.usarMock) {
        throw new ErroApi('NAO_IMPLEMENTADO', 501)
      }

      return exigirResposta(
        requisitar<RespostasTesteResponse>(
          `testes-nivel/${encodeURIComponent(testeId)}/respostas`,
          {
            method: 'POST',
            body: JSON.stringify(payload),
          },
        ),
      )
    },
  }
}

export const apiTestes = criarApiTestes(configuracao)