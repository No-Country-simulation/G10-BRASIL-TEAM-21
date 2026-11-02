import { NavLink, Outlet } from 'react-router-dom'

import { textos } from '../texts/pt-BR'

export default function Layout() {
  return (
    <>
      <header className="cabecalho">
        <NavLink className="marca" to="/upload">
          {textos.marca}
        </NavLink>

        <nav className="navegacao" aria-label={textos.navegacao.aria}>
          <NavLink to="/upload">{textos.navegacao.upload}</NavLink>
          <NavLink to="/historico">{textos.navegacao.historico}</NavLink>
          <NavLink to="/perfil">{textos.navegacao.perfil}</NavLink>
          <NavLink to="/login">{textos.navegacao.login}</NavLink>
        </nav>
      </header>

      <main className="conteudo-principal">
        <Outlet />
      </main>

      <footer className="rodape">{textos.rodape}</footer>
    </>
  )
}
