const CHAVE_TOKEN = 'adaptai-access-token'

export const obterTokenAcesso = (): string | null => {
  return localStorage.getItem(CHAVE_TOKEN)
}

export function definirTokenAcesso(valor: string | null) {
  if (valor) {
    localStorage.setItem(CHAVE_TOKEN, valor)
  } else {
    localStorage.removeItem(CHAVE_TOKEN)
  }
}