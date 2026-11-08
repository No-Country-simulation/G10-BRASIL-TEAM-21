import { Link, useLocation } from 'react-router-dom'
import { useUsuario } from '../../contexts/usuario-context'
import { textos } from '../../texts/pt-BR'
import { iniciais } from '../../utils/usuario'
import { ThemeToggle } from './ThemeToggle'

interface HeaderProps {
  menuAberto: boolean
  aoAbrirMenu: () => void
}

const titulos: [string, string][] = [
  ['/painel', textos.navegacao.painel],
  ['/upload', textos.navegacao.upload],
  ['/historico', textos.navegacao.historico],
  ['/perfil', textos.navegacao.perfil],
  ['/resultado', textos.navegacao.resultado],
]

export function Header({ menuAberto, aoAbrirMenu }: HeaderProps) {
  const { pathname } = useLocation()
  const { usuario } = useUsuario()

  const paginaAtual =
    titulos.find(([rota]) => pathname.startsWith(rota))?.[1] ??
    textos.navegacao.painel

  return (
    <header className="app-header">
      <div className="app-header-start">
        <button
          type="button"
          className="app-menu-button"
          onClick={aoAbrirMenu}
          aria-label={textos.navegacao.abrirMenu}
          aria-expanded={menuAberto}
          aria-controls="menu-lateral"
        >
          <i className="bi bi-list" aria-hidden="true" />
        </button>

        <nav className="app-breadcrumb" aria-label="Você está em">
          <span>{textos.navegacao.breadcrumbRaiz}</span>
          <i className="bi bi-chevron-right" aria-hidden="true" />
          <strong aria-current="page">{paginaAtual}</strong>
        </nav>
      </div>

      <div className="app-header-end">
        <ThemeToggle />

        <Link
          to="/perfil"
          className="app-avatar app-avatar-link"
          aria-label={textos.navegacao.perfil}
          title={usuario?.nome ?? textos.navegacao.perfil}
        >
          {iniciais(usuario?.nome)}
        </Link>
      </div>
    </header>
  )
}
