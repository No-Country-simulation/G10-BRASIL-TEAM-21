import type { components } from './schema'

// Apenas aliases: os modelos de domínio são gerados pelo OpenAPI.
export type Adaptacao = components['schemas']['AdaptacaoResponse']
export type AdaptacaoRequest = components['schemas']['AdaptacaoRequest']
export type ErroResposta = components['schemas']['ErroResposta']
export type Documento = components['schemas']['DocumentoResponse']
export type ItemConteudo =
  components['schemas']['ConteudoAdaptado']['itens'][number]
