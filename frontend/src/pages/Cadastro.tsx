import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiAutenticacao } from '../api/autenticacao'
import type { CadastroRequest } from '../api/tipos'
import { AuthLayout } from '../components/auth/AuthLayout'
import { textos } from '../texts/pt-BR'

export default function Cadastro() {
  const t = textos.auth
  const navigate = useNavigate()

  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [nivel, setNivel] =
    useState<CadastroRequest['nivel_declarado']>('Iniciante')

  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  useEffect(() => {
    document.title = 'Criar conta | AdaptAI'
  }, [])

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
        erroApi instanceof Error ? erroApi.message : textos.erros.DESCONHECIDO,
      )
    } finally {
      setCarregando(false)
    }
  }

  return (
    <AuthLayout
      modo="cadastro"
      titulo={t.lateralCadastro.titulo}
      descricao={t.lateralCadastro.descricao}
      destaques={t.lateralCadastro.destaques}
    >
      <h1>{t.criar}</h1>
      <p className="auth-card-description">{t.criarDescricao}</p>

      {erro && (
        <p className="auth-alert auth-alert-error" role="alert">
          <i className="bi bi-exclamation-circle" aria-hidden="true" />
          <span>{erro}</span>
        </p>
      )}

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="auth-field">
          <label htmlFor="nome">{t.nome}</label>
          <input
            id="nome"
            name="nome"
            className="auth-input"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            autoComplete="name"
            required
            maxLength={200}
          />
        </div>

        <div className="auth-field">
          <label htmlFor="email">{t.email}</label>
          <input
            id="email"
            name="email"
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
              name="senha"
              className="auth-input"
              type={mostrarSenha ? 'text' : 'password'}
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              autoComplete="new-password"
              aria-describedby="senha-dica"
              required
              minLength={8}
              maxLength={128}
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
          <span id="senha-dica" className="auth-field-hint">
            {t.dicaSenha}
          </span>
        </div>

        <div className="auth-field">
          <label htmlFor="nivel">{t.nivel}</label>
          <select
            id="nivel"
            name="nivel_declarado"
            className="auth-select"
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
        </div>

        <button
          type="submit"
          className="auth-button auth-button-block"
          disabled={carregando}
        >
          {carregando ? 'Criando conta...' : t.criar}
        </button>
      </form>

      <p className="auth-switch">
        {t.temConta} <Link to="/login">{t.entrar}</Link>
      </p>
    </AuthLayout>
  )
}
