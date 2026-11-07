import { criarClienteHttp } from './cliente'
import { configuracao } from './configuracao'
import { ErroApi } from './erros'
import { obterTokenAcesso } from './sessao'
import type {
  CadastroRequest,
  CadastroResponse,
  LoginRequest,
  LoginResponse,
} from './tipos'

const requisitar = criarClienteHttp(configuracao, obterTokenAcesso)

async function exigirResposta<T>(promessa: Promise<T | undefined>,): Promise<T> {
  const resposta = await promessa

  if (!resposta) {
    throw new ErroApi('RESPOSTA_INVALIDA')
  }

  return resposta
}

export const apiAutenticacao = {
  async login(dados: LoginRequest): Promise<LoginResponse> {
    return exigirResposta(
      requisitar<LoginResponse>('auth/login', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    )
  },

  async cadastrar(dados: CadastroRequest): Promise<CadastroResponse> {
    return exigirResposta(
      requisitar<CadastroResponse>('auth/cadastro', {
        method: 'POST',
        body: JSON.stringify(dados),
      }),
    )
  },
}