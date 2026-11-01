import { useSearchParams } from 'react-router-dom'

import { configuracao } from '../api/configuracao'

export type Estado = 'carregando' | 'vazio' | 'erro' | 'sucesso'

export function useEstadoMock(): Estado {
  const [params] = useSearchParams()
  const estado = configuracao.usarMock ? params.get('estado') : null

  if (estado === 'carregando' || estado === 'vazio' || estado === 'erro') {
    return estado
  }

  return 'sucesso'
}
