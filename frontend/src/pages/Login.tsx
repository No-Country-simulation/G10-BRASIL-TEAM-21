import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { apiAutenticacao } from '../api/autenticacao'
import { definirTokenAcesso, obterTokenAcesso } from '../api/sessao'
import { AuthLayout } from '../components/auth/AuthLayout'
import { textos } from '../texts/pt-BR'
import { configuracaoDemo } from '../config/demo'

type LoginState = { mensagem?: string; email?: string } | null

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const t = textos.auth

  /* Dados enviados pelo Cadastro após criar a conta */
  const estado = location.state as LoginState
  const mensagem = estado?.mensagem ?? ''

  const [email, setEmail] = useState(estado?.email ?? '')
  const [senha, setSenha] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')

  useEffect(() => {
    document.title = 'Entrar | AdaptAI'
  }, [])

  /* Quem já está logado vai direto para o painel */
  if (obterTokenAcesso()) {
    return <Navigate to="/painel" replace />
  }

  async function realizarLogin(emailLogin: string, senhaLogin: string) {
    setErro('')
    setCarregando(true)

    try {
      const resposta = await apiAutenticacao.login({
        email: emailLogin,
        senha: senhaLogin,
      })

      definirTokenAcesso(resposta.access_token)

      navigate('/painel', { replace: true })
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
    await realizarLogin(configuracaoDemo.email, configuracaoDemo.senha)
  }

  return (
    <AuthLayout
      modo="login"
      titulo={t.lateralLogin.titulo}
      descricao={t.lateralLogin.descricao}
      destaques={t.lateralLogin.destaques}
    >
      <h1>{t.entrar}</h1>
      <p className="auth-card-description">{t.introducao}</p>

      {mensagem && !erro && (
        <p className="auth-alert auth-alert-success" role="status">
          <i className="bi bi-check-circle" aria-hidden="true" />
          <span>{mensagem}</span>
        </p>
      )}

      {erro && (
        <p className="auth-alert auth-alert-error" role="alert">
          <i className="bi bi-exclamation-circle" aria-hidden="true" />
          <span>{erro}</span>
        </p>
      )}

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="auth-field">
          <label htmlFor="email">{t.email}</label>
          <input
            id="email"
            className="auth-input"
            type="email"
            placeholder={t.placeholderEmail}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </div>

        <div className="auth-field">
          <label htmlFor="senha">{t.senha}</label>
          <div className="auth-password">
            <input
              id="senha"
              className="auth-input"
              type={mostrarSenha ? 'text' : 'password'}
              placeholder={t.placeholderSenha}
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              autoComplete="current-password"
              required
            />
            <button
              type="button"
              className="auth-password-toggle"
              onClick={() => setMostrarSenha((atual) => !atual)}
              aria-label={mostrarSenha ? t.ocultarSenha : t.mostrarSenha}
              aria-pressed={mostrarSenha}
            >
              <i className={`bi ${mostrarSenha ? 'bi-eye-slash' : 'bi-eye'}`} />
            </button>
          </div>
        </div>

        <button
          type="submit"
          className="auth-button auth-button-block"
          disabled={carregando}
        >
          {carregando ? 'Entrando...' : t.entrar}
        </button>

        {configuracaoDemo.habilitado && (
          <>
            <div className="auth-divider">{t.ou}</div>
            <button
              type="button"
              className="auth-button auth-button-secondary auth-button-block"
              onClick={handleDemoLogin}
              disabled={carregando}
            >
              {carregando ? 'Entrando...' : 'Entrar com conta de demonstração'}
            </button>
          </>
        )}
      </form>

      <p className="auth-switch">
        {t.semConta} <Link to="/cadastro">{t.cadastrar}</Link>
      </p>
    </AuthLayout>
  )
}
