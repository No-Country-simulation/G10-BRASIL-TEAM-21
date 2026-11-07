import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiAutenticacao } from '../api/autenticacao'
import { definirTokenAcesso } from '../api/sessao'
import { textos } from '../texts/pt-BR'
import { configuracaoDemo } from '../config/demo'

export default function Login() {
  const navigate = useNavigate()
  const t = textos.auth

  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')

  async function realizarLogin(emailLogin: string, senhaLogin: string) {
  setErro('')
  setCarregando(true)

  try {
    const resposta = await apiAutenticacao.login({
      email: emailLogin,
      senha: senhaLogin,
    })

    definirTokenAcesso(resposta.access_token)

    navigate('/upload', { replace: true })
  } catch (error) {
    setErro(
      error instanceof Error
        ? error.message
        : 'Não foi possível realizar o login. Tente novamente.',
    )
  } finally {
    setCarregando(false)
  }
}

async function handleSubmit(e: FormEvent<HTMLFormElement>) {
  e.preventDefault()
  await realizarLogin(email, senha)
}

async function handleDemoLogin() {
  await realizarLogin(
    configuracaoDemo.email,
    configuracaoDemo.senha,
  )
}
  
return (
  <main className="pagina-autenticacao">
    <section className="painel-autenticacao">
      <h1>{textos.marca}</h1>

      <p>{t.introducao}</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="email">{t.email}</label>

        <input
          id="email"
          type="email"
          placeholder={t.placeholderEmail}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
        />

        <label htmlFor="senha">{t.senha}</label>

        <input
          id="senha"
          type="password"
          placeholder={t.placeholderSenha}
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          autoComplete="current-password"
          required
        />

        {erro && (
          <p className="text-danger" role="alert">
            {erro}
          </p>
        )}

        <button type="submit" disabled={carregando}>
          {carregando ? 'Entrando...' : t.entrar}
        </button>

        {configuracaoDemo.habilitado && (
          <button
            type="button"
            onClick={handleDemoLogin}
            disabled={carregando}
          >
            {carregando
              ? 'Entrando...'
              : 'Entrar com conta de demonstração'}
          </button>
        )}
      </form>

      <p>
        {t.semConta} <Link to="/cadastro">{t.cadastrar}</Link>
      </p>
    </section>
  </main>
)
}