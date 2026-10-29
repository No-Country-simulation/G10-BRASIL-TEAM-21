import type { ReactNode } from 'react'
import type { Estado } from '../hooks/useEstadoMock'

interface EstadoTelaProps {
  estado: Estado
  children: ReactNode
  mensagemVazia?: string
  mensagemErro?: string
  aoTentarNovamente?: () => void
}

export function EstadoTela({
  estado,
  children,
  mensagemVazia = 'Nenhum conteúdo disponível.',
  mensagemErro = 'Não foi possível carregar esta página.',
  aoTentarNovamente = () => window.location.reload(),
}: EstadoTelaProps) {
  if (estado === 'carregando') {
    return (
      <div className="estado" role="status" aria-live="polite">
        <span className="carregando" />
        <p>Carregando informações...</p>
      </div>
    )
  }

  if (estado === 'vazio') {
    return (
      <div className="estado">
        <h2>Nada por aqui ainda</h2>
        <p>{mensagemVazia}</p>
      </div>
    )
  }

  if (estado === 'erro') {
    return (
      <div className="estado" role="alert">
        <h2>Não foi possível concluir</h2>
        <p>{mensagemErro}</p>
        <button type="button" onClick={aoTentarNovamente}>
          Tentar novamente
        </button>
      </div>
    )
  }

  return <>{children}</>
}
