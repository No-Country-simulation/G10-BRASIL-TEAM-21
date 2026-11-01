import type { ReactNode } from 'react'
import type { Estado } from '../hooks/useEstadoMock'
import type { ErroApi } from '../api/erros'
import { textos } from '../texts/pt-BR'

interface EstadoTelaProps {
  estado: Estado
  children: ReactNode
  mensagemVazia?: string
  mensagemErro?: string
  erro?: ErroApi
  aoTentarNovamente?: () => void
}

export function EstadoTela({
  estado,
  children,
  mensagemVazia = textos.estados.vazioPadrao,
  mensagemErro = textos.estados.erroPadrao,
  erro,
  aoTentarNovamente = () => window.location.reload(),
}: EstadoTelaProps) {
  if (estado === 'carregando')
    return (
      <div className="estado" role="status" aria-live="polite">
        <span className="carregando" />
        <p>{textos.estados.carregando}</p>
      </div>
    )
  if (estado === 'vazio')
    return (
      <div className="estado">
        <h2>{textos.estados.vazio}</h2>
        <p>{mensagemVazia}</p>
      </div>
    )
  if (estado === 'erro')
    return (
      <div className="estado" role="alert">
        <h2>{textos.estados.erro}</h2>
        <p>{erro?.message ?? mensagemErro}</p>
        {erro?.detalhes.length ? (
          <ul>
            {erro.detalhes.map((item, i) => (
              <li key={i}>
                {item.campo ? `${item.campo}: ` : ''}
                {textos.erros.VALIDACAO_FALHOU}
              </li>
            ))}
          </ul>
        ) : null}
        {erro?.requestId && (
          <small>
            {textos.estados.referencia}: {erro.requestId}
          </small>
        )}
        <button type="button" onClick={aoTentarNovamente}>
          {textos.estados.tentar}
        </button>
      </div>
    )
  return <>{children}</>
}
