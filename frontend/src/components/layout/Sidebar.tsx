import { NavLink, useNavigate } from 'react-router-dom'
import { apiAutenticacao } from '../../api/autenticacao'
import { definirTokenAcesso } from '../../api/sessao'
import { useUsuario } from '../../contexts/usuario-context'
import { textos } from '../../texts/pt-BR'
import { iniciais } from '../../utils/usuario'

interface SidebarProps {
  aberto: boolean
  aoNavegar: () => void
}

const itens = [
  { to: '/painel', icone: 'bi-grid-1x2', rotulo: textos.navegacao.painel },
  { to: '/upload', icone: 'bi-plus-lg', rotulo: textos.navegacao.upload },
  { to: '/historico', icone: 'bi-clock-history', rotulo: textos.navegacao.historico },
  { to: '/perfil', icone: 'bi-person', rotulo: textos.navegacao.perfil },
]

export function Sidebar({ aberto, aoNavegar }: SidebarProps) {
  const navigate = useNavigate()
  const { usuario } = useUsuario()

  async function sair() {
    try {
      await apiAutenticacao.logout()
    } catch {
    } finally {
      definirTokenAcesso(null)
      navigate('/login', { replace: true })
    }
  }

  return (
    <aside
      id="menu-lateral"
      className={`app-sidebar ${aberto ? 'is-open' : ''}`}
      aria-label={textos.navegacao.aria}
    >
      <NavLink to="/painel" className="app-brand" onClick={aoNavegar}>
        <img src="/Icon.png" alt="" />
        <span>
          Adapt<span>AI</span>
        </span>
      </NavLink>

      <nav className="app-nav">
        <span className="app-nav-label">{textos.navegacao.espaco}</span>

        {itens.map((item) => (
          <NavLink key={item.to} to={item.to} onClick={aoNavegar}>
            <i className={`bi ${item.icone}`} aria-hidden="true" />
            {item.rotulo}
          </NavLink>
        ))}
      </nav>

      <div className="app-user">
        <span className="app-avatar" aria-hidden="true">
          {iniciais(usuario?.nome)}
        </span>

        <div className="app-user-info">
          <strong>{usuario?.nome ?? 'Minha conta'}</strong>
          {usuario?.email && <span>{usuario.email}</span>}
        </div>

        <button
          type="button"
          className="app-user-logout"
          onClick={sair}
          aria-label={textos.navegacao.sair}
          title={textos.navegacao.sair}
        >
          <i className="bi bi-box-arrow-right" aria-hidden="true" />
        </button>
      </div>
    </aside>
  )
}
