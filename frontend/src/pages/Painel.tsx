import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { configuracao } from '../api/configuracao'
import type { AdaptacoesListResponse, Perfil } from '../api/tipos'
import { apiAdaptacoes } from '../api/adaptacoes'
import { apiUsuario } from '../api/usuario'
import { useUsuario } from '../contexts/usuario-context'
import { textos } from '../texts/pt-BR'
import { primeiroNome } from '../utils/usuario'
import '../styles/painel.css'

type EstadoPerfil =
  | { status: 'carregando' }
  | { status: 'ok'; perfil: Perfil }
  | { status: 'indisponivel' }

type EstadoAdaptacoes =
  | { status: 'carregando' }
  | { status: 'ok'; dados: AdaptacoesListResponse }
  | { status: 'erro' }

type Formato = keyof typeof textos.opcoes.formatos

const iconesFormato: Record<Formato, string> = {
  Tutorial: 'bi-book',
  Flashcards: 'bi-layers',
  Quiz: 'bi-bullseye',
  Resumo: 'bi-file-earmark-text',
  'Roteiro de Aula': 'bi-mortarboard',
}

const formatos = Object.keys(textos.opcoes.formatos) as Formato[]

const dataHoje = new Intl.DateTimeFormat('pt-BR', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
}).format(new Date())

export default function Painel() {
  const t = textos.painel
  const { usuario } = useUsuario()
  const [perfil, setPerfil] = useState<EstadoPerfil>({status: 'carregando',})
  const [adaptacoes, setAdaptacoes] = useState<EstadoAdaptacoes>({status: 'carregando',})
  
  useEffect(() => {
    document.title = 'Painel | AdaptAI'
  }, [])

  /* O perfil de evolução ainda pode estar indisponível na API: o painel segue funcional */
  useEffect(() => {
      let ativo = true

      apiUsuario
        .obterPerfil()
        .then((dados) => {
          if (ativo) setPerfil({ status: 'ok', perfil: dados })
        })
        .catch(() => {
          if (ativo) setPerfil({ status: 'indisponivel' })
        })

      return () => {
        ativo = false
      }
    }, [])

    
    /* Carrega as adaptações reais quando a aplicação está conectada à API. */
  const carregarAdaptacoes = useCallback(async (signal?: AbortSignal) => {
    if (configuracao.usarMock) return

    setAdaptacoes({ status: 'carregando' })

    try {
      const dados = await apiAdaptacoes.listar(5, 0, signal)
      setAdaptacoes({ status: 'ok', dados })
    } catch (erro) {
      if (erro instanceof Error && erro.name === 'AbortError') return

      setAdaptacoes({ status: 'erro' })
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    void carregarAdaptacoes(controller.signal)

    return () => controller.abort()
  }, [carregarAdaptacoes])

  const nome = primeiroNome(usuario?.nome)
  const nivelAtual = perfil.status === 'ok'? perfil.perfil.nivel_atual : usuario?.nivel_atual
  const rotuloNivel = nivelAtual? textos.opcoes.niveis[nivelAtual as keyof typeof textos.opcoes.niveis] : null

  return (
    <div className="painel">
      <header className="painel-head">
        <div>
          <span className="painel-eyebrow">{dataHoje}</span>
          <h1>{nome ? `${t.saudacao}, ${nome}.` : t.saudacaoSemNome}</h1>
          <p>{t.subtitulo}</p>
        </div>

        <Link to="/upload" className="app-button">
          <i className="bi bi-plus-lg" aria-hidden="true" />
          {t.novaAdaptacao}
        </Link>
      </header>

      <div className="painel-grid">
        <div className="painel-main">
          <section className="painel-card painel-hero" aria-labelledby="inicio-rapido">
            <span className="painel-badge">
              <i className="bi bi-stars" aria-hidden="true" />
              {t.inicioRapido.selo}
            </span>
            <h2 id="inicio-rapido">{t.inicioRapido.titulo}</h2>
            <p>{t.inicioRapido.descricao}</p>
            <Link to="/upload" className="app-button">
              {t.inicioRapido.acao}
              <i className="bi bi-arrow-right" aria-hidden="true" />
            </Link>
          </section>

          <section aria-labelledby="formatos">
            <div className="painel-section-head">
              <h2 id="formatos">{t.formatos.titulo}</h2>
            </div>

            <div className="painel-formatos">
              {formatos.map((formato) => (
                <Link
                  key={formato}
                  to={`/upload?formato=${encodeURIComponent(formato)}`}
                  className="painel-formato"
                >
                  <span className="painel-icone">
                    <i className={`bi ${iconesFormato[formato]}`} aria-hidden="true" />
                  </span>
                  <strong>{textos.opcoes.formatos[formato]}</strong>
                  <span>{t.formatos.descricoes[formato]}</span>
                </Link>
              ))}
            </div>
          </section>

          <section aria-labelledby="recentes">
            <div className="painel-section-head">
              <h2 id="recentes">{t.recentes.titulo}</h2>
              <Link to="/historico" className="painel-link">
                {t.recentes.verTodas}
                <i className="bi bi-arrow-right" aria-hidden="true" />
              </Link>
            </div>

            {configuracao.usarMock ? (
              <Link to="/resultado/demo-1" className="painel-recente">
                <span className="painel-icone">
                  <i className="bi bi-layers" aria-hidden="true" />
                </span>
                <span className="painel-recente-texto">
                  <strong>{t.recentes.exemploTitulo}</strong>
                  <span>{t.recentes.exemploMeta}</span>
                </span>
                <i className="bi bi-arrow-right" aria-hidden="true" />
              </Link>
            ) : adaptacoes.status === 'carregando' ? (
              <div className="painel-vazio" aria-live="polite" aria-busy="true">
                <span className="painel-icone">
                  <i className="bi bi-arrow-repeat" aria-hidden="true" />
                </span>
                <div>
                  <strong>Carregando adaptações...</strong>
                  <p>Buscando suas adaptações na API.</p>
                </div>
              </div>
            ) : adaptacoes.status === 'erro' ? (
              <div className="painel-vazio" role="alert">
                <span className="painel-icone">
                  <i className="bi bi-exclamation-circle" aria-hidden="true" />
                </span>
                <div>
                  <strong>Não foi possível carregar as adaptações.</strong>
                  <p>Verifique sua conexão e tente novamente mais tarde.</p>
                </div>
              </div>
            ) : adaptacoes.dados.itens.length > 0 ? (
              <div>
                {adaptacoes.dados.itens.map((adaptacao) => (
                  <Link
                    key={adaptacao.adaptacao_id}
                    to={`/resultado/${encodeURIComponent(adaptacao.adaptacao_id)}`}
                    className="painel-recente"
                  >
                    <span className="painel-icone">
                      <i className="bi bi-file-earmark-text" aria-hidden="true" />
                    </span>

                    <span className="painel-recente-texto">
                      <strong>{adaptacao.titulo}</strong>
                      <span>
                        {adaptacao.formato_gerado} · {adaptacao.perfil_aplicado}
                        {' · '}
                        {formatarData(adaptacao.criado_em)}
                      </span>
                    </span>

                    <i className="bi bi-arrow-right" aria-hidden="true" />
                  </Link>
                ))}
              </div>
            ) : (
              <div className="painel-vazio">
                <span className="painel-icone">
                  <i className="bi bi-clock-history" aria-hidden="true" />
                </span>
                <div>
                  <strong>{t.recentes.vazioTitulo}</strong>
                  <p>{t.recentes.vazioDescricao}</p>
                </div>
                <Link to="/upload" className="app-button app-button-small">
                  {t.recentes.vazioAcao}
                </Link>
              </div>
            )}
          </section>
        </div>

        <aside className="painel-side" aria-label="Resumo da sua evolução">
          <section className="painel-card" aria-labelledby="progresso">
            <span className="painel-eyebrow" id="progresso">
              {t.progresso.titulo}
            </span>

            {perfil.status === 'carregando' && (
              <div className="painel-skeleton" aria-busy="true">
                <span />
                <span />
                <span />
              </div>
            )}

            {perfil.status === 'ok' && (
              <ProgressoXp perfil={perfil.perfil} rotuloNivel={rotuloNivel} />
            )}

            {perfil.status === 'indisponivel' && (
              <>
                <p className="painel-nota">{t.progresso.indisponivel}</p>
              </>
            )}
          </section>

          {perfil.status === 'ok' && perfil.perfil.teste_nivel_disponivel && (
            <section className="painel-card painel-teste" aria-labelledby="teste">
              <span className="painel-badge painel-badge-warm">{t.teste.selo}</span>
              <h2 id="teste">{t.teste.titulo}</h2>
              <p>{t.teste.descricao}</p>
              <Link to="/perfil" className="painel-link">
                {t.teste.acao}
                <i className="bi bi-arrow-right" aria-hidden="true" />
              </Link>
            </section>
          )}

          {rotuloNivel && (
            <section className="painel-perfil" aria-labelledby="perfil-atual">
              <span className="painel-eyebrow" id="perfil-atual">
                {t.perfilAtual.titulo}
              </span>
              <h2>{rotuloNivel}</h2>
              <p>{t.perfilAtual.descricao}</p>
              <Link to="/perfil" className="painel-link">
                {t.perfilAtual.acao}
                <i className="bi bi-arrow-right" aria-hidden="true" />
              </Link>
            </section>
          )}
        </aside>
      </div>
    </div>
  )
}

function ProgressoXp({
  perfil,
  rotuloNivel,
}: {
  perfil: Perfil
  rotuloNivel: string | null
}) {
  const t = textos.painel.progresso
  const percentual = Math.min(Math.max(perfil.progresso_percentual, 0), 100)
  const restantes = Math.max(perfil.xp_para_proximo_nivel - perfil.xp_total, 0)

  return (
    <>
      <p className="painel-xp">
        {perfil.xp_total.toLocaleString('pt-BR')} <small>XP</small>
      </p>
      {rotuloNivel && (
        <p className="painel-nivel">
          {t.nivel} {rotuloNivel}
        </p>
      )}

      <div
        className="painel-barra"
        role="progressbar"
        aria-valuenow={Math.round(percentual)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={t.titulo}
      >
        <span style={{ width: `${percentual}%` }} />
      </div>

      <div className="painel-barra-info">
        <span>{t.proximoMarco}</span>
        <span>
          {restantes.toLocaleString('pt-BR')} {t.restantes}
        </span>
      </div>
    </>
  )
}

function formatarData(data: string): string {
  const valor = new Date(data)

  if (Number.isNaN(valor.getTime())) {
    return 'Data não disponível'
  }

  return valor.toLocaleDateString('pt-BR')
}
