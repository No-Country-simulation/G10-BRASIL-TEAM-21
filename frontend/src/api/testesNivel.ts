
import { criarClienteHttp } from './cliente'
import { configuracao } from './configuracao'
import { ErroApi } from './erros'
import { obterTokenAcesso } from './sessao'
import type {
  TesteNivelResponse,
  RespostasTesteRequest,
  RespostasTesteResponse,
} from './tipos'

const requisitar = criarClienteHttp(configuracao, obterTokenAcesso)

async function exigirResposta<T>(
  promessa: Promise<T | undefined>,
): Promise<T> {
  const resposta = await promessa

  if (!resposta) {
    throw new ErroApi('RESPOSTA_INVALIDA')
  }

  return resposta
}

export const apiTestesNivel = {
  iniciar(): Promise<TesteNivelResponse> {
    return exigirResposta(
      requisitar<TesteNivelResponse>('testes/nivel', {
        method: 'POST',
      }),
    )
  },

  responder(
    testeId: string,
    payload: RespostasTesteRequest,
  ): Promise<RespostasTesteResponse> {
    return exigirResposta(
      requisitar<RespostasTesteResponse>(
        `testes/nivel/${encodeURIComponent(testeId)}/respostas`,
        {
          method: 'POST',
          body: JSON.stringify(payload),
        },
      ),
    )
  },
}
