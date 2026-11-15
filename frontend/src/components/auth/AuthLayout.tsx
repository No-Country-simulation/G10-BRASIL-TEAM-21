import { useState } from 'react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ThemeToggle } from '../layout/ThemeToggle'
import '../../styles/auth.css'

type AuthLayoutProps = {
  /** Define o link de ação do cabeçalho (Entrar ⇄ Criar conta) */
  modo: 'login' | 'cadastro'
  /** Título grande do painel lateral (mesmo estilo do hero da Home) */
  titulo: ReactNode
  /** Frase de apoio abaixo do título */
  descricao: string
  /** Pontos de valor exibidos no painel lateral */
  destaques: readonly string[]
  children: ReactNode
}

/* Mesmo trecho em três profundidades (versão compacta da demonstração da Home) */
const niveisDemo = [
  {
    id: 'iniciante',
    label: 'Iniciante',
    text: 'Pense na VPC como o condomínio fechado da sua empresa na nuvem: só entra quem você autoriza, e você decide como as ruas, as sub-redes, se conectam.',
  },
  {
    id: 'intermediario',
    label: 'Intermediário',
    text: 'A VPC isola seus recursos na nuvem. Você divide esse espaço em sub-redes, controla as rotas entre elas e define quem acessa o quê com regras de segurança.',
  },
  {
    id: 'avancado',
    label: 'Avançado',
    text: 'A VPC define o limite lógico de rede da conta: bloco CIDR, sub-redes por zona de disponibilidade, tabelas de rota e controles de tráfego por ACL e security group.',
  },
] as const

export function AuthLayout({
  modo,
  titulo,
  descricao,
  destaques,
  children,
}: AuthLayoutProps) {
  const ehLogin = modo === 'login'
  const [nivel, setNivel] = useState(1)

  return (
    <div className="auth-page">
      <header className="auth-header">
        <nav className="auth-nav auth-container" aria-label="Navegação">
          <Link className="auth-logo" to="/" aria-label="AdaptAI, voltar ao início">
            <img src="/Icon.png" alt="" />
            <span>
              Adapt<span>AI</span>
            </span>
          </Link>

          <div className="auth-nav-actions">
            <Link to="/" className="auth-nav-link auth-nav-back">
              <i className="bi bi-arrow-left" aria-hidden="true" /> Início
            </Link>
            <ThemeToggle />
            <Link
              to={ehLogin ? '/cadastro' : '/login'}
              className={ehLogin ? 'auth-button auth-button-small' : 'auth-nav-link'}
            >
              {ehLogin ? 'Criar conta' : 'Entrar'}
            </Link>
          </div>
        </nav>
      </header>

      <main className="auth-main auth-container">
        <aside className="auth-aside">
          <p className="auth-aside-title">{titulo}</p>
          <p className="auth-aside-text">{descricao}</p>

          <ul className="auth-points">
            {destaques.map((item) => (
              <li key={item}>
                <i className="bi bi-check2-circle" aria-hidden="true" />
                <span>{item}</span>
              </li>
            ))}
          </ul>

          <div className="auth-preview">
            <div className="auth-preview-bar">
              <span>
                <i className="bi bi-file-earmark-text" aria-hidden="true" />
                documentacao-tecnica.pdf
              </span>
              <span className="auth-preview-tag">Exemplo</span>
            </div>

            <div className="auth-preview-body">
              <div
                className="auth-preview-levels"
                role="group"
                aria-label="Nível de explicação"
              >
                {niveisDemo.map((item, index) => (
                  <button
                    key={item.id}
                    type="button"
                    aria-pressed={index === nivel}
                    className={index === nivel ? 'active' : ''}
                    onClick={() => setNivel(index)}
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              {/* Os três textos ocupam a mesma célula: a altura fica fixa e nada "pula" ao trocar */}
              <div className="auth-preview-answers" aria-live="polite">
                {niveisDemo.map((item, index) => (
                  <p
                    key={item.id}
                    className={index === nivel ? 'active' : ''}
                    aria-hidden={index !== nivel}
                  >
                    {item.text}
                  </p>
                ))}
              </div>

              <span className="auth-preview-source">
                <i className="bi bi-check2-circle" aria-hidden="true" /> Baseado
                no trecho original
              </span>
            </div>
          </div>
        </aside>

        <section className="auth-card">{children}</section>
      </main>
    </div>
  )
}
