import { textos } from '../texts/pt-BR'
import type { ErroResposta } from './tipos'

export class ErroApi extends Error {
  readonly codigo: string
  readonly status: number
  readonly requestId?: string
  readonly detalhes: NonNullable<ErroResposta['detalhes']>

  constructor(
    codigo: string,
    status = 0,
    requestId?: string,
    detalhes: NonNullable<ErroResposta['detalhes']> = [],
  ) {
    super(
      textos.erros[codigo as keyof typeof textos.erros] ??
        textos.erros.DESCONHECIDO,
    )
    this.name = 'ErroApi'
    this.codigo = codigo
    this.status = status
    this.requestId = requestId
    this.detalhes = detalhes
  }
}

export function normalizarErro(corpo: unknown, status: number): ErroApi {
  const dados =
    corpo && typeof corpo === 'object' ? (corpo as Record<string, unknown>) : {}
  // Compatibilidade temporária com o cadastro atual; o contrato usa EMAIL_JA_CADASTRADO.
  const codigo =
    dados.codigo === 'EMAIL_EXISTE' ? 'EMAIL_JA_CADASTRADO' : dados.codigo
  const detalhes = Array.isArray(dados.detalhes)
    ? dados.detalhes.filter(
        (item): item is NonNullable<ErroResposta['detalhes']>[number] =>
          !!item &&
          typeof item === 'object' &&
          typeof item.mensagem === 'string' &&
          (item.campo == null || typeof item.campo === 'string'),
      )
    : []
  return new ErroApi(
    typeof codigo === 'string'
      ? codigo
      : status === 401
        ? 'NAO_AUTENTICADO'
        : 'DESCONHECIDO',
    status,
    typeof dados.request_id === 'string' ? dados.request_id : undefined,
    detalhes,
  )
}
