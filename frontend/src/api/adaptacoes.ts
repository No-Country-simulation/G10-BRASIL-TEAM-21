import { criarClienteHttp } from './cliente'
import { configuracao, type ConfiguracaoApi } from './configuracao'
import { ErroApi } from './erros'
import type { OpcoesMock } from './mock'
import { obterTokenAcesso } from './sessao'
import type { Adaptacao, AdaptacaoRequest, Documento } from './tipos'

export function criarApiAdaptacoes(
  config: ConfiguracaoApi,
  obterToken = obterTokenAcesso,
  transporte: typeof fetch = fetch,
) {
  const requisitar = criarClienteHttp(config, obterToken, transporte)
  let recente: Adaptacao | undefined

  async function exigirResposta<T>(
    promessa: Promise<T | undefined>,
  ): Promise<T> {
    const resposta = await promessa
    if (!resposta) throw new ErroApi('RESPOSTA_INVALIDA')
    return resposta
  }

  return {
    async obter(
      id: string,
      signal?: AbortSignal,
      mock?: OpcoesMock,
    ): Promise<Adaptacao> {
      if (config.usarMock) {
        const { obterMock } = await import('./mock')
        return obterMock(mock, signal)
      }
      if (id === 'recente') {
        if (!recente) throw new ErroApi('RECURSO_NAO_ENCONTRADO', 404)
        return recente
      }
      return exigirResposta(
        requisitar<Adaptacao>(`adaptacoes/${encodeURIComponent(id)}`, {
          signal,
        }),
      )
    },
    async gerar(
      payload: AdaptacaoRequest,
      signal?: AbortSignal,
    ): Promise<Adaptacao> {
      if (config.usarMock) {
        if (payload.formato_saida !== 'Flashcards')
          throw new ErroApi('NAO_IMPLEMENTADO', 501)
        const { obterMock } = await import('./mock')
        recente = await obterMock({}, signal)
      } else {
        recente = await exigirResposta(
          requisitar<Adaptacao>('adaptacoes', {
            method: 'POST',
            body: JSON.stringify(payload),
            signal,
          }),
        )
      }
      return recente
    },
    async enviarDocumento(
      arquivo: File,
    ): Promise<Documento> {
      if (config.usarMock) throw new ErroApi('NAO_IMPLEMENTADO', 501)
      const body = new FormData()
      body.set('arquivo', arquivo)
      return exigirResposta(
        requisitar<Documento>('documentos', {
          method: 'POST',
          body,
        }),
      )
    },
  }
}

export const apiAdaptacoes = criarApiAdaptacoes(configuracao)
