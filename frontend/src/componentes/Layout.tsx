import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <>
      <header className="cabecalho">
        <a className="marca" href="/upload">AdaptAI</a>

        <nav className="navegacao" aria-label="Navegação principal">
          <NavLink to="/upload">Novo conteúdo</NavLink>
          <NavLink to="/historico">Histórico</NavLink>
          <NavLink to="/perfil">Meu perfil</NavLink>
        </nav>
      </header>

      <main className="conteudo-principal">
        <Outlet />
      </main>

      <footer className="rodape">
        AdaptAI · Aprendizagem adaptativa
      </footer>
    </>
  )
}
