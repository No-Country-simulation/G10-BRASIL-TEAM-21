import { ErroApi, normalizarErro } from './erros'
import type { ConfiguracaoApi } from './configuracao'

export function criarClienteHttp(
  config: ConfiguracaoApi,
  obterToken: () => string | null = () => null,
  transporte: typeof fetch = fetch,
) {
  return async function requisitar<T>(
    caminho: string,
    opcoes: RequestInit = {},
  ): Promise<T | undefined> {
    const headers = new Headers(opcoes.headers)
    headers.set('Accept', 'application/json')
    if (typeof opcoes.body === 'string')
      headers.set('Content-Type', 'application/json')
    const token = obterToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
    let resposta: Response
    try {
      resposta = await transporte(
        `${config.url}/${caminho.replace(/^\/+/, '')}`,
        { ...opcoes, headers },
      )
    } catch (erro) {
      if (erro instanceof Error && erro.name === 'AbortError') throw erro
      throw new ErroApi('CONEXAO_INDISPONIVEL')
    }
    if (resposta.status === 204) return undefined
    let corpo: unknown
    try {
      corpo = await resposta.json()
    } catch {
      throw new ErroApi(
        resposta.ok ? 'RESPOSTA_INVALIDA' : 'DESCONHECIDO',
        resposta.status,
      )
    }
    if (!resposta.ok) throw normalizarErro(corpo, resposta.status)
    return corpo as T
  }
}
