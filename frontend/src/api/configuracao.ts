export interface ConfiguracaoApi {
  usarMock: boolean
  url: string
}

export function lerConfiguracao(env: {
  VITE_USE_MOCK?: string
  VITE_API_URL?: string
}): ConfiguracaoApi {
  return {
    usarMock: env.VITE_USE_MOCK === 'true',
    url: (env.VITE_API_URL?.trim() || '/api/v1').replace(/\/+$/, ''),
  }
}

export const configuracao = lerConfiguracao(import.meta.env)
