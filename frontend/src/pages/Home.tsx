import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent } from 'react'
import { Link } from 'react-router-dom'
import { ThemeToggle } from '../components/layout/ThemeToggle'
import { useReveal } from '../hooks/useReveal'
import '../styles/home.css'

/* ---------- Conteúdo ---------- */

const diferenciais = [
  {
    title: 'Explicação no seu nível',
    description:
      'O mesmo trecho é explicado de um jeito para quem está começando e de outro para quem já trabalha com o assunto.',
  },
  {
    title: 'Analogias do seu contexto',
    description:
      'Conceitos abstratos são comparados a situações que você já conhece.',
  },
  {
    title: 'Fonte sempre visível',
    description:
      'Cada explicação indica o trecho do documento de onde veio, para você conferir.',
  },
  {
    title: 'Progresso acompanhado',
    description: 'Veja o que você já dominou e o que ainda precisa revisar.',
  },
]

type SampleLine = { text: string; correct?: boolean }

const formatos: {
  title: string
  description: string
  detail: string
  sampleLabel: string
  sample: SampleLine[]
}[] = [
  {
    title: 'Tutorial',
    description: 'Aprenda em etapas',
    detail:
      'O documento vira um passo a passo, com cada conceito explicado na ordem certa.',
    sampleLabel: 'Exemplo de tutorial',
    sample: [
      { text: '1. Criar a rede virtual' },
      { text: '2. Dividir a rede em sub-redes' },
      { text: '3. Definir as regras de acesso' },
    ],
  },
  {
    title: 'Flashcards',
    description: 'Fixe os conceitos',
    detail:
      'Perguntas e respostas curtas extraídas do material, para revisar rápido.',
    sampleLabel: 'Exemplo de flashcard',
    sample: [
      { text: 'Para que serve uma sub-rede?' },
      { text: 'Dividir a rede em partes menores e isolar recursos.' },
    ],
  },
  {
    title: 'Quiz',
    description: 'Teste o que aprendeu',
    detail:
      'Questões baseadas no seu documento, com explicação e o trecho de origem.',
    sampleLabel: 'Qual recurso controla o tráfego de uma sub-rede?',
    sample: [
      { text: 'Tabela de rotas', correct: false },
      { text: 'Regras de acesso', correct: true },
      { text: 'Bloco de endereços', correct: false },
    ],
  },
  {
    title: 'Resumo',
    description: 'Vá direto ao essencial',
    detail:
      'Os pontos principais do material em poucos parágrafos, com referência à fonte.',
    sampleLabel: 'Exemplo de resumo',
    sample: [
      {
        text: 'Uma VPC isola seus recursos na nuvem. Ela é dividida em sub-redes, e as regras de acesso definem quem se conecta a quê.',
      },
    ],
  },
  {
    title: 'Roteiro de aula',
    description: 'Ensine com clareza',
    detail:
      'Uma sequência pronta para explicar o conteúdo a outras pessoas.',
    sampleLabel: 'Exemplo de roteiro',
    sample: [
      { text: 'Abertura (5 min): o problema que a VPC resolve' },
      { text: 'Explicação (15 min): sub-redes e rotas' },
      { text: 'Prática (10 min): montar uma rede simples' },
    ],
  },
]

const etapas = [
  {
    title: 'Envie o documento',
    description: 'Adicione o material que você precisa estudar.',
  },
  {
    title: 'Informe seu perfil',
    description:
      'Diga sua área e escolha entre cinco níveis, de iniciante a especialista.',
  },
  {
    title: 'Escolha o formato e estude',
    description: 'Receba o conteúdo adaptado e acompanhe seu progresso.',
  },
]

const perguntas = [
  {
    q: 'De onde vêm as respostas e explicações?',
    a: 'O conteúdo é construído com base no material enviado. Você pode consultar a fonte utilizada em cada conceito.',
  },
  {
    q: 'Preciso conhecer o assunto antes?',
    a: 'Não. A adaptação considera o nível de conhecimento informado para apresentar o conteúdo de forma adequada.',
  },
  {
    q: 'Quais formatos de aprendizagem estão disponíveis?',
    a: 'Tutoriais, flashcards, quizzes, resumos e roteiros de aula.',
  },
  {
    q: 'Posso acompanhar minha evolução?',
    a: 'Sim. O AdaptAI acompanha seu progresso e apoia sua evolução durante os estudos.',
  },
]

/* Mesmo trecho explicado em três profundidades (demonstração do hero) */
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
]

/* ---------- Página ---------- */

function Home() {
  useReveal()

  useEffect(() => {
    document.title = 'AdaptAI | Aprenda qualquer documento no seu nível'
  }, [])

  const [nivel, setNivel] = useState(0)
  const [activeFormat, setActiveFormat] = useState(0)
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([])

  const format = formatos[activeFormat]
  const demo = niveisDemo[nivel]

  /* Navegação por teclado nas abas (setas, Home, End) */
  const handleTabKey = (event: KeyboardEvent<HTMLButtonElement>) => {
    const last = formatos.length - 1
    let next = activeFormat

    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
      next = activeFormat === last ? 0 : activeFormat + 1
    } else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
      next = activeFormat === 0 ? last : activeFormat - 1
    } else if (event.key === 'Home') {
      next = 0
    } else if (event.key === 'End') {
      next = last
    } else {
      return
    }

    event.preventDefault()
    setActiveFormat(next)
    tabRefs.current[next]?.focus()
  }

  return (
    <div className="home-page">
      <header className="home-header">
        <nav className="home-nav home-container">

          <a className="home-logo" href="#inicio" aria-label="AdaptAI, início">
            <img
              src="/Icon.png"
              alt=""
              className="adaptai"
            />
            <span>
              Adapt<span>AI</span>
            </span>
          </a>

          <div className="home-nav-links">
            <a href="#diferenciais">O que muda</a>
            <a href="#formatos">Formatos</a>
            <a href="#como-funciona">Como funciona</a>
            <a href="#faq">FAQ</a>
          </div>

          <div className="home-nav-actions">
            <ThemeToggle />
            <Link to="/login" className="home-login">
              Entrar
            </Link>
            <Link to="/cadastro" className="home-button home-button-small">
              Criar conta
            </Link>
          </div>
        </nav>
      </header>

      <main>
        {/* ============ HERO ============ */}
        <section className="home-hero home-container" id="inicio">
          <div className="home-hero-content">
            <h1>
              Documentação densa.
              <br />
              Aprendizado seu.
            </h1>

            <p>
              Envie um documento técnico e receba tutoriais, flashcards, quizzes
              e resumos no seu nível, com o trecho original ao lado de cada
              explicação.
            </p>

            <div className="home-hero-actions">
              <Link to="/cadastro" className="home-button">
                Começar gratuitamente
              </Link>
              <a href="#como-funciona" className="home-secondary-link">
                Ver como funciona
              </a>
            </div>

            <div className="home-trust">
              <i className="bi bi-shield-check" />
              Todo conteúdo é gerado a partir do material que você enviar.
            </div>
          </div>

          {/* Demonstração do produto: o mesmo trecho, três níveis */}
          <div className="home-preview">
            <div className="mock">
              <div className="mock-bar">
                <span className="mock-file">
                  <i className="bi bi-file-earmark-text" />
                  documentacao-tecnica.pdf
                </span>
                <span className="mock-tag">Exemplo</span>
              </div>

              <div className="mock-body">
                <div className="mock-pane mock-doc">
                  <span className="mock-label">Documento original</span>
                  <p>
                    Antes de criar recursos, defina a estrutura de rede da conta.{' '}
                    <mark>
                      Uma VPC é uma rede virtual isolada dentro da nuvem, na qual
                      você define sub-redes, tabelas de rota e regras de acesso.
                    </mark>{' '}
                    Cada sub-rede pode ser pública ou privada, conforme a
                    necessidade da aplicação.
                  </p>
                </div>

                <div className="mock-pane">
                  <span className="mock-label">Explicação para você</span>

                  <div className="mock-levels" role="group" aria-label="Nível de explicação">
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

                  <p className="mock-answer" key={demo.id} aria-live="polite">
                    {demo.text}
                  </p>

                  <span className="mock-source">
                    <i className="bi bi-check2-circle" /> Baseado no trecho destacado
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ============ DIFERENCIAIS ============ */}
        <section className="home-section" id="diferenciais">
          <div className="home-container home-split">
            <div className="home-section-heading" data-reveal>
              <h2>Entenda o documento sem precisar relê-lo.</h2>
              <p>O material continua o mesmo. O que muda é a explicação, o formato e o ritmo.</p>
            </div>

            <div className="home-feature-grid" data-reveal>
              {diferenciais.map((item) => (
                <article className="home-feature" key={item.title}>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* ============ FORMATOS ============ */}
        <section className="home-section home-section-alt" id="formatos">
          <div className="home-container">
            <div className="home-section-heading" data-reveal>
              <h2>Um documento, cinco formatos de estudo.</h2>
              <p>Escolha o formato que combina com o que você precisa agora.</p>
            </div>

            <div className="format-layout" data-reveal>
              <div
                className="format-tabs"
                role="tablist"
                aria-orientation="vertical"
                aria-label="Formatos de estudo"
              >
                {formatos.map((item, index) => (
                  <button
                    key={item.title}
                    ref={(el) => {
                      tabRefs.current[index] = el
                    }}
                    type="button"
                    role="tab"
                    id={`formato-tab-${index}`}
                    aria-selected={index === activeFormat}
                    aria-controls="formato-panel"
                    tabIndex={index === activeFormat ? 0 : -1}
                    className={index === activeFormat ? 'active' : ''}
                    onClick={() => setActiveFormat(index)}
                    onKeyDown={handleTabKey}
                  >
                    <strong>{item.title}</strong>
                    <span>{item.description}</span>
                  </button>
                ))}
              </div>

              <div
                className="format-panel"
                key={activeFormat}
                role="tabpanel"
                id="formato-panel"
                aria-labelledby={`formato-tab-${activeFormat}`}
              >
                <h3>{format.title}</h3>
                <p>{format.detail}</p>

                <div className="format-sample">
                  <span className="sample-label">{format.sampleLabel}</span>
                  {format.sample.map((line) => (
                    <div
                      key={line.text}
                      className={`sample-line ${line.correct ? 'correct' : ''}`}
                    >
                      {line.correct !== undefined && (
                        <i
                          className={`bi ${
                            line.correct ? 'bi-check-circle-fill' : 'bi-circle'
                          }`}
                        />
                      )}
                      <span>{line.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ============ COMO FUNCIONA ============ */}
        <section className="home-section" id="como-funciona">
          <div className="home-container">
            <div className="home-section-heading" data-reveal>
              <h2>Da documentação à descoberta.</h2>
              <p>Três passos para transformar informação em conhecimento.</p>
            </div>

            <div className="home-steps" data-reveal>
              {etapas.map((step, index) => (
                <article className="home-step" key={step.title}>
                  <span className="home-step-number">{index + 1}</span>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* ============ FAQ ============ */}
        <section className="home-section home-section-alt" id="faq">
          <div className="home-container home-faq-content">
            <div className="home-faq-heading" data-reveal>
              <h2>Perguntas frequentes</h2>
              <p>Entenda melhor como o AdaptAI funciona.</p>
            </div>

            <div className="home-faq-list" data-reveal>
              {perguntas.map((item) => (
                <details key={item.q}>
                  <summary>{item.q}</summary>
                  <p>{item.a}</p>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* ============ CTA ============ */}
        <section className="home-cta">
          <div className="home-container" data-reveal>
            <h2>Comece com um documento.</h2>
            <p>Crie sua conta e transforme o primeiro material em conteúdo de estudo.</p>
            <Link to="/cadastro" className="home-button home-button-light">
              Criar conta
            </Link>
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <div className="home-container home-footer-content">
          <div className="home-footer-brand">
            <a className="home-logo" href="#inicio" aria-label="AdaptAI, início">
              Adapt<span>AI</span>
            </a>
            <p>© {new Date().getFullYear()} AdaptAI. Todos os direitos reservados.</p>
          </div>

          <nav className="home-footer-links" aria-label="Rodapé">
            <Link to="/termos">Termos de uso</Link>
            <Link to="/privacidade">Política de privacidade</Link>
            <a href="mailto:contato@adaptai.com">Contato</a>
          </nav>
        </div>
      </footer>
    </div>
  )
}

export default Home