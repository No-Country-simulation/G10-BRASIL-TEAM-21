import exemplo from '../mocks/adaptacao-flashcards.json'
import { ErroApi } from './erros'
import type { Adaptacao } from './tipos'

export type CenarioMock =
  'completo' | 'nulos' | 'vazio' | 'erro' | 'carregando' | 'pendente' | 'falha'
export interface OpcoesMock {
  cenario?: CenarioMock
  codigo?: string
}

export function montarExemplo({
  cenario = 'completo',
}: OpcoesMock = {}): Adaptacao {
  // A fixture também é validada contra o JSON Schema do OpenAPI nos testes.
  const dados = structuredClone(exemplo) as Adaptacao
  if (cenario === 'nulos') {
    dados.analogias = null
    dados.microlearning = null
    dados.trilha_evolucao = null
    dados.metadados.nivel_documento_estimado = null
    dados.metadados.dominio_conhecimento = null
    dados.metadados.alerta_descompasso = false
    dados.avaliacao_qualidade.fidelidade_analogias_score = null
  }
  if (cenario === 'vazio') dados.conteudo_adaptado.itens = []
  if (cenario === 'pendente' || cenario === 'falha')
    dados.armazenamento_oci.status_upload = cenario
  return dados
}

export async function obterMock(
  opcoes: OpcoesMock = {},
  signal?: AbortSignal,
): Promise<Adaptacao> {
  await new Promise<void>((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException('Aborted', 'AbortError'))
      return
    }
    const concluir = () => {
      signal?.removeEventListener('abort', cancelar)
      resolve()
    }
    const timer =
      opcoes.cenario === 'carregando' ? undefined : setTimeout(concluir, 250)
    function cancelar() {
      if (timer !== undefined) clearTimeout(timer)
      signal?.removeEventListener('abort', cancelar)
      reject(new DOMException('Aborted', 'AbortError'))
    }
    signal?.addEventListener('abort', cancelar, { once: true })
  })
  if (opcoes.cenario === 'erro')
    throw new ErroApi(
      opcoes.codigo || 'BANCO_INDISPONIVEL',
      503,
      'req-mock-erro',
    )
  return montarExemplo(opcoes)
}
