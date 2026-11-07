
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiAutenticacao } from '../api/autenticacao'
import type { CadastroRequest } from '../api/tipos'
import { textos } from '../texts/pt-BR'

export default function Cadastro() {
  const t = textos.auth
  const navigate = useNavigate()

  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [nivel, setNivel] =
    useState<CadastroRequest['nivel_declarado']>('Iniciante')

  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setErro('')
    setCarregando(true)

    try {
      await apiAutenticacao.cadastrar({
        nome,
        email,
        senha,
        nivel_declarado: nivel,
      })

      console.log('Cadastro concluído! Redirecionando para login...')

      navigate('/login', {
        replace: true,
        state: {
          mensagem: 'Cadastro realizado com sucesso! Faça login para continuar.',
          email,
        },
      })
    } catch (erroApi) {
      setErro(
        erroApi instanceof Error
          ? erroApi.message
          : textos.erros.DESCONHECIDO,
      )
    } finally {
      setCarregando(false)
    }
  }

  return (
    <main className="pagina-autenticacao">
      <section className="painel-autenticacao">
        <h1>{t.criar}</h1>
        <p>{t.criarDescricao}</p>

        {erro && (
          <p className="aviso" role="alert">
            {erro}
          </p>
        )}

        <form onSubmit={handleSubmit}>
          <label htmlFor="nome">{t.nome}</label>
          <input
            id="nome"
            name="nome"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            autoComplete="name"
            required
            maxLength={200}
          />

          <label htmlFor="email">{t.email}</label>
          <input
            id="email"
            name="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />

          <label htmlFor="senha">{t.senha}</label>
          <input
            id="senha"
            name="senha"
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            autoComplete="new-password"
            required
            minLength={8}
            maxLength={128}
          />

          <label htmlFor="nivel">{t.nivel}</label>
          <select
            id="nivel"
            name="nivel_declarado"
            value={nivel}
            onChange={(e) =>
              setNivel(e.target.value as CadastroRequest['nivel_declarado'])
            }
          >
            {Object.entries(textos.opcoes.niveis)
              .filter(([valor]) => valor !== 'Gestor/Executivo')
              .map(([valor, rotulo]) => (
                <option key={valor} value={valor}>
                  {rotulo}
                </option>
              ))}
          </select>

          <button type="submit" disabled={carregando}>
            {carregando ? 'Criando conta...' : t.criar}
          </button>
        </form>

        <p>
          {t.temConta} <Link to="/login">{t.entrar}</Link>
        </p>
      </section>
    </main>
  )
}
