import { criarClienteHttp } from './cliente'
import { configuracao } from './configuracao'
import { ErroApi } from './erros'
import { obterTokenAcesso } from './sessao'
import type { Perfil, Usuario } from './tipos'

const requisitar = criarClienteHttp(configuracao, obterTokenAcesso)

async function exigirResposta<T>(promessa: Promise<T | undefined>): Promise<T> {
  const resposta = await promessa

  if (!resposta) {
    throw new ErroApi('RESPOSTA_INVALIDA')
  }

  return resposta
}

export const apiUsuario = {
  /** Dados da conta logada (nome, e-mail e nível). */
  obterAtual(): Promise<Usuario> {
    return exigirResposta(requisitar<Usuario>('usuarios/me'))
  },

  /** Perfil de evolução (XP, nível e próximo marco). */
  obterPerfil(): Promise<Perfil> {
    return exigirResposta(requisitar<Perfil>('perfil'))
  },
}
