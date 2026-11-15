import { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { UsuarioProvider } from '../../contexts/UsuarioProvider'
import { textos } from '../../texts/pt-BR'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import '../../styles/app-shell.css'

export default function Layout() {
  const [menuAberto, setMenuAberto] = useState(false)

  useEffect(() => {
    if (!menuAberto) return

    const aoPressionar = (evento: KeyboardEvent) => {
      if (evento.key === 'Escape') setMenuAberto(false)
    }

    window.addEventListener('keydown', aoPressionar)
    return () => window.removeEventListener('keydown', aoPressionar)
  }, [menuAberto])

  return (
    <UsuarioProvider>
      <div className="app-shell">
        <a className="app-skip" href="#conteudo-principal">
          {textos.navegacao.pularConteudo}
        </a>

        <Sidebar aberto={menuAberto} aoNavegar={() => setMenuAberto(false)} />

        {menuAberto && (
          <button
            type="button"
            className="app-overlay"
            aria-label={textos.navegacao.fecharMenu}
            onClick={() => setMenuAberto(false)}
          />
        )}

        <div className="app-main">
          <Header menuAberto={menuAberto} aoAbrirMenu={() => setMenuAberto(true)} />

          <main className="app-content" id="conteudo-principal" tabIndex={-1}>
            <Outlet />
          </main>
        </div>
      </div>
    </UsuarioProvider>
  )
}
