import { Link } from 'react-router-dom'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'

export default function Login() {
  const estado = useEstadoMock()

  return (
    <main className="pagina-autenticacao">
      <section className="painel-autenticacao">
        <EstadoTela
          estado={estado}
          mensagemVazia="O formulário de acesso não está disponível."
          mensagemErro="Não foi possível carregar o acesso à conta."
        >
          <>
            <h1>AdaptAI</h1>
            <p>Entre para adaptar conteúdos ao seu nível de conhecimento.</p>

            <form onSubmit={(e) => e.preventDefault()}>
              <label htmlFor="email">E-mail</label>
              <input id="email" type="email" placeholder="seu@email.com" required />

              <label htmlFor="senha">Senha</label>
              <input id="senha" type="password" placeholder="Sua senha" required />

              <button type="submit">Entrar</button>
            </form>

            <p>Ainda não tem conta? <Link to="/cadastro">Cadastre-se</Link></p>
          </>
        </EstadoTela>
      </section>
    </main>
  )
}
