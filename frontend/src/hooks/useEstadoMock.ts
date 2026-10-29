import { useSearchParams } from 'react-router-dom'

export type Estado = 'carregando' | 'vazio' | 'erro' | 'sucesso'

export function useEstadoMock(): Estado {
  const [params] = useSearchParams()
  const estado = params.get('estado')

  if (
    estado === 'carregando' ||
    estado === 'vazio' ||
    estado === 'erro'
  ) {
    return estado
  }

  return 'sucesso'
}
