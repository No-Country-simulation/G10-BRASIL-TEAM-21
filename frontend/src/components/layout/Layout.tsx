import {Outlet} from 'react-router-dom'
import {textos} from '../../texts/pt-BR'
import {Sidebar} from './Sidebar'
import {Header} from './Header'

export default function Layout() {
  return (
    <div className="app-layout">

      <Sidebar />

      <div className="app-main">

        <Header />

        <main className="conteudo-principal">
          <Outlet />
        </main>

        <footer className="rodape">
          {textos.rodape}
        </footer>

      </div>

    </div>
  )
}