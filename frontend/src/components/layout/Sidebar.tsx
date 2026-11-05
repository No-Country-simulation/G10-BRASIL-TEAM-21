import { NavLink } from 'react-router-dom'
import { textos } from '../../texts/pt-BR'

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <i className="bi bi-stars" />
        <span>{textos.marca}</span>
      </div>

      <nav className="nav flex-column">
        <NavLink to="/upload">
          <i className="bi bi-file-earmark-plus" />
          {textos.navegacao.upload}
        </NavLink>

        <NavLink to="/historico">
          <i className="bi bi-clock-history" />
          {textos.navegacao.historico}
        </NavLink>

        <NavLink to="/perfil">
          <i className="bi bi-person" />
          {textos.navegacao.perfil}
        </NavLink>
      </nav>
    </aside>
  )
}