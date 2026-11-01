import { Link } from 'react-router-dom'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'
import { textos } from '../texts/pt-BR'

export default function Login() {
  const estado = useEstadoMock()
  const t = textos.auth
  return (
    <main className="pagina-autenticacao">
      <section className="painel-autenticacao">
        <EstadoTela estado={estado} mensagemVazia={t.vazioLogin}>
          <h1>{textos.marca}</h1>
          <p>{t.introducao}</p>
          <form onSubmit={(e) => e.preventDefault()}>
            <label htmlFor="email">{t.email}</label>
            <input
              id="email"
              type="email"
              placeholder={t.placeholderEmail}
              required
            />
            <label htmlFor="senha">{t.senha}</label>
            <input
              id="senha"
              type="password"
              placeholder={t.placeholderSenha}
              required
            />
            <button type="submit" disabled>
              {t.entrar}
            </button>
          </form>
          <p>{t.wireframe}</p>
          <p>
            {t.semConta} <Link to="/cadastro">{t.cadastrar}</Link>
          </p>
          <Link to="/upload">{textos.navegacao.upload}</Link>
        </EstadoTela>
      </section>
    </main>
  )
}
