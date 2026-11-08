import type { components } from './api-types'

// Tipos derivados automaticamente do contrato OpenAPI.
export type AdaptacaoResponse = components['schemas']['AdaptacaoResponse']
export type LoginRequest = components['schemas']['LoginRequest']

// Aliases utilizados atualmente pela aplicação.
export type Adaptacao = AdaptacaoResponse
export type AdaptacaoRequest = components['schemas']['AdaptacaoRequest']
export type ErroResposta = components['schemas']['ErroResposta']
export type Documento = components['schemas']['DocumentoResponse']
export type ItemConteudo = components['schemas']['ConteudoAdaptado']['itens'][number]
export type LoginResponse =  components['schemas']['LoginResponse']
export type CadastroRequest = components['schemas']['CadastroRequest']
export type CadastroResponse = components['schemas']['CadastroResponse']
export type Usuario = components['schemas']['UsuarioMeResponse']
export type Perfil = components['schemas']['PerfilResponse']
