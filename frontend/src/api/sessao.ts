// Sessão volátil: o fluxo de autenticação pode fornecer o token sem persistir em disco.
let token: string | null = null
export const obterTokenAcesso = () => token
export function definirTokenAcesso(valor: string | null) {
  token = valor
}
