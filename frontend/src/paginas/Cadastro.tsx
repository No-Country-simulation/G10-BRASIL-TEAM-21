import { Link } from 'react-router-dom'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'

const niveis = ['Iniciante', 'Basico', 'Intermediario', 'Avancado', 'Especialista']

export default function Cadastro() {
  const estado = useEstadoMock()

  return (
    <main className="pagina-autenticacao">
      <section className="painel-autenticacao">
        <EstadoTela
          estado={estado}
          mensagemVazia="O formulário de cadastro não está disponível."
          mensagemErro="Não foi possível carregar o cadastro."
        >
          <>
            <h1>Criar conta</h1>
            <p>Informe seus dados para começar a usar o AdaptAI.</p>

            <form onSubmit={(e) => e.preventDefault()}>
              <label htmlFor="nome">Nome</label>
              <input id="nome" name="nome" required />

              <label htmlFor="email">E-mail</label>
              <input id="email" name="email" type="email" required />

              <label htmlFor="senha">Senha</label>
              <input id="senha" name="senha" type="password" required />

              <label htmlFor="nivel">Nível de conhecimento</label>
              <select id="nivel" name="nivel_declarado" defaultValue="Iniciante">
                {niveis.map((nivel) => <option key={nivel} value={nivel}>{nivel}</option>)}
              </select>

              <button type="submit">Criar conta</button>
            </form>

            <p>Já tem uma conta? <Link to="/login">Entrar</Link></p>
          </>
        </EstadoTela>
      </section>
    </main>
  )
}
