import { Link } from 'react-router-dom'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'
import { textos } from '../texts/pt-BR'

export default function Cadastro() {
  const estado = useEstadoMock()
  const t = textos.auth
  return (
    <main className="pagina-autenticacao">
      <section className="painel-autenticacao">
        <EstadoTela estado={estado} mensagemVazia={t.vazioCadastro}>
          <h1>{t.criar}</h1>
          <p>{t.criarDescricao}</p>
          <form onSubmit={(e) => e.preventDefault()}>
            <label htmlFor="nome">{t.nome}</label>
            <input id="nome" name="nome" required maxLength={200} />
            <label htmlFor="email">{t.email}</label>
            <input id="email" name="email" type="email" required />
            <label htmlFor="senha">{t.senha}</label>
            <input
              id="senha"
              name="senha"
              type="password"
              required
              minLength={8}
              maxLength={128}
            />
            <label htmlFor="nivel">{t.nivel}</label>
            <select id="nivel" name="nivel_declarado" defaultValue="Iniciante">
              {Object.entries(textos.opcoes.niveis)
                .filter(([valor]) => valor !== 'Gestor/Executivo')
                .map(([valor, rotulo]) => (
                  <option key={valor} value={valor}>
                    {rotulo}
                  </option>
                ))}
            </select>
            <button type="submit" disabled>
              {t.criar}
            </button>
          </form>
          <p>{t.wireframe}</p>
          <p>
            {t.temConta} <Link to="/login">{t.entrar}</Link>
          </p>
        </EstadoTela>
      </section>
    </main>
  )
}
