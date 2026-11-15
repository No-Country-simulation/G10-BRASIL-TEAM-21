import { useState, type ReactNode } from 'react'
import type { Adaptacao, ItemConteudo } from '../api/tipos'
import { textos } from '../texts/pt-BR'

const t = textos.resultado
const percentual = (valor: number) =>
  `${Math.round(Math.max(0, Math.min(1, valor)) * 100)}%`
const lista = (itens: string[]) => itens.join(', ') || t.nenhum

function obterAnalogiaRef(item: ItemConteudo): string | null {
  if ('analogia_ref' in item && typeof item.analogia_ref === 'string') {
    return item.analogia_ref
  }

  return null
}

function ItemAdaptado({
  item,
  onQuizConfirmado,
}: {
  item: ItemConteudo
  onQuizConfirmado?: () => void
}) {
  const [versoVisivel, setVersoVisivel] = useState(false)
  const [alternativaSelecionada, setAlternativaSelecionada] = useState<
    string | null
  >(null)
  const [quizConfirmado, setQuizConfirmado] = useState(false)

  if ('frente' in item) {
    const analogia = obterAnalogiaRef(item)
    return (
      <article className="flashcard-card">
        <button
          type="button"
          className="flashcard"
          data-verso={versoVisivel}
          onClick={() => setVersoVisivel((v) => !v)}
          aria-label={
            versoVisivel
              ? 'Voltar para a frente do flashcard'
              : 'Revelar resposta do flashcard'
          }
          aria-expanded={versoVisivel}
        >
          <span className="flashcard-status">
            {versoVisivel ? 'Resposta' : 'Pergunta'}
          </span>
          <span className="flashcard-conteudo">
            {versoVisivel ? item.verso : item.frente}
          </span>
          <span className="flashcard-instrucao">
            {versoVisivel ? 'Toque para voltar' : 'Toque para revelar'}
          </span>
        </button>

        {versoVisivel && item.dica_didatica && (
          <p className="flashcard-dica">
            <strong>{t.dica}:</strong> {item.dica_didatica}
          </p>
        )}

        <footer className="flashcard-rodape">
          <span className="chip">{item.conceito_ref}</span>
          {analogia && <span className="chip">{analogia}</span>}
          <details className="flashcard-fontes">
            <summary>{t.fontes}</summary>
            {lista(item.fontes_chunks)}
          </details>
        </footer>
      </article>
    )
  }

  if ('pergunta' in item) {
    const respostaDisponivel = Boolean(item.resposta_correta)
    const acertou =
      respostaDisponivel && alternativaSelecionada === item.resposta_correta
    const analogia = obterAnalogiaRef(item)

    return (
      <article className="quiz-card">
        <span className="quiz-status">Quiz</span>

        <h2 className="quiz-pergunta">{item.pergunta}</h2>

        <div
          className="quiz-alternativas"
          role="group"
          aria-label="Alternativas"
        >
          {item.alternativas.map((alternativa) => {
            const selecionada = alternativaSelecionada === alternativa.id
            const correta =
              quizConfirmado &&
              respostaDisponivel &&
              alternativa.id === item.resposta_correta
            const incorreta =
              quizConfirmado && respostaDisponivel && selecionada && !acertou

            return (
              <button
                key={alternativa.id}
                type="button"
                className={[
                  'quiz-alternativa',
                  selecionada ? 'selecionada' : '',
                  correta ? 'correta' : '',
                  incorreta ? 'incorreta' : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={() => {
                  if (!quizConfirmado) setAlternativaSelecionada(alternativa.id)
                }}
                disabled={quizConfirmado}
                aria-pressed={selecionada}
              >
                <span className="quiz-alternativa-id">
                  {alternativa.id.toUpperCase()}
                </span>
                <span className="quiz-alternativa-texto">
                  {alternativa.texto}
                </span>
                {correta && <span aria-label="Resposta correta">✓</span>}
                {incorreta && <span aria-label="Resposta incorreta">✕</span>}
              </button>
            )
          })}
        </div>

        {!quizConfirmado ? (
          <button
            type="button"
            className="botao-confirmar-quiz"
            disabled={!alternativaSelecionada}
            onClick={() => {
              setQuizConfirmado(true)
              onQuizConfirmado?.()
            }}
          >
            Confirmar resposta
          </button>
        ) : (
          <div
            className={`quiz-feedback ${acertou ? 'feedback-correto' : 'feedback-incorreto'}`}
            role="status"
          >
            {respostaDisponivel ? (
              <>
                <strong>
                  {acertou ? 'Resposta correta!' : 'Resposta incorreta.'}
                </strong>
                {!acertou && (
                  <p>
                    Resposta correta: {item.resposta_correta?.toUpperCase()}
                  </p>
                )}
              </>
            ) : (
              <strong>Resposta registrada. Gabarito não disponível.</strong>
            )}
            {item.justificativa && <p>{item.justificativa}</p>}
          </div>
        )}

        <footer className="flashcard-rodape">
          <span className="chip">{item.conceito_ref}</span>
          {analogia && <span className="chip">{analogia}</span>}
          <details className="flashcard-fontes">
            <summary>{t.fontes}</summary>
            {lista(item.fontes_chunks)}
          </details>
        </footer>
      </article>
    )
  }

  return (
    <article className="cartao">
      {'passo' in item && (
        <>
          <h2>
            {t.passo} {item.passo}: {item.titulo}
          </h2>
          <p>{item.instrucao}</p>
          {item.exemplo && (
            <p>
              {t.exemplo}: {item.exemplo}
            </p>
          )}
        </>
      )}

      {'topico' in item && (
        <>
          <h2>{item.topico}</h2>
          <p>{item.resumo}</p>
          <p>
            <strong>{t.impacto}:</strong> {item.impacto_negocio}
          </p>
        </>
      )}

      {'bloco' in item && (
        <>
          <h2>
            {t.bloco} {item.bloco}: {item.titulo}
          </h2>
          <p>{item.fala}</p>
          <p>
            {item.duracao_min} {t.minutos}
          </p>
          {item.recurso_visual && (
            <p>
              {t.recurso}: {item.recurso_visual}
            </p>
          )}
        </>
      )}

      <small>
        {t.conceito}: {item.conceito_ref}
      </small>

      {obterAnalogiaRef(item) && (
        <small>
          {t.analogiaRef}: {obterAnalogiaRef(item)}
        </small>
      )}

      <small>
        {t.fontes}: {lista(item.fontes_chunks)}
      </small>
    </article>
  )
}

export function PacoteAdaptacao({
  dados,
  children,
}: {
  dados: Adaptacao
  children?: ReactNode
}) {
  const [confirmados, setConfirmados] = useState<Set<number>>(new Set())
  const [resetKey, setResetKey] = useState(0)

  const itens = dados.conteudo_adaptado.itens
  const totalQuizzes = itens.filter((i) => 'pergunta' in i).length
  const todosRespondidos = totalQuizzes > 0 && confirmados.size === totalQuizzes

  const reiniciarQuiz = () => {
    setConfirmados(new Set())
    setResetKey((k) => k + 1)
  }

  const m = dados.metadados
  const q = dados.avaliacao_qualidade
  const trilha = dados.trilha_evolucao
  const status = dados.armazenamento_oci?.status_upload ?? 'pendente'

  return (
    <>
      <h1>{dados.conteudo_adaptado.titulo}</h1>
      <p>{dados.conteudo_adaptado.introducao_contextualizada}</p>
      {dados.cache_hit && <p role="status">{t.cache}</p>}
      <section className="cartao" aria-label={t.titulo}>
        <dl className="metadados">
          <dt>{t.formato}</dt>
          <dd>{m.formato_gerado}</dd>
          <dt>{t.perfil}</dt>
          <dd>{textos.opcoes.niveis[m.perfil_aplicado]}</dd>
          <dt>{t.nicho}</dt>
          <dd>{textos.opcoes.nichos[m.nicho_aplicado]}</dd>
          <dt>{t.detalhe}</dt>
          <dd>{textos.opcoes.detalhes[m.nivel_detalhe]}</dd>
          {m.dominio_conhecimento && (
            <>
              <dt>{t.dominio}</dt>
              <dd>{m.dominio_conhecimento}</dd>
            </>
          )}
          <dt>{t.tempo}</dt>
          <dd>
            {m.tempo_estimado_estudo_minutos} {t.minutos}
          </dd>
          <dt>{t.nivelDocumento}</dt>
          <dd>
            {m.nivel_documento_estimado
              ? textos.opcoes.niveis[m.nivel_documento_estimado]
              : t.desconhecido}
          </dd>
          <dt>{t.conceitos}</dt>
          <dd>{lista(m.conceitos_chave)}</dd>
          <dt>{t.requisitos}</dt>
          <dd>{lista(m.pre_requisitos)}</dd>
        </dl>
      </section>
      {m.alerta_descompasso && m.nivel_documento_estimado != null && (
        <aside className="aviso" role="status">
          <strong>{t.descompasso}</strong>
          <p>{t.descompassoDescricao}</p>
        </aside>
      )}
      {status !== 'concluido' ? (
        <aside className="aviso" role="status">
          <strong>{t.armazenamento}</strong>
          <p>{t[status]}</p>
        </aside>
      ) : (
        <p className="sucesso" role="status">
          {t.concluido}
        </p>
      )}
      <div className="lista-cartoes">
        {itens.map((item, i) => (
          <ItemAdaptado
            key={`${i}-${resetKey}`}
            item={item}
            onQuizConfirmado={() =>
              setConfirmados((prev) => new Set(prev).add(i))
            }
          />
        ))}
      </div>
      <section className="cartao">
        <h2>{t.qualidade}</h2>
        <p>
          {t.ancoragem}: <strong>{percentual(q.ancoragem_fonte_score)}</strong>
        </p>
        <progress
          aria-label={t.ancoragem}
          max="1"
          value={Math.max(0, Math.min(1, q.ancoragem_fonte_score))}
        />
        {q.ancoragem_fonte_score < 0.8 && (
          <p className="aviso">{t.scoreBaixo}</p>
        )}
        {q.fidelidade_analogias_score != null && (
          <p>
            {t.fidelidade}: {percentual(q.fidelidade_analogias_score)}
          </p>
        )}
        <p>
          {t.clareza}: {q.clareza_pedagogica}
        </p>
        <p>
          {t.chunks}: {q.chunks_utilizados}
        </p>
        <p>
          {t.buscaHibrida}: {q.busca_hibrida ? t.sim : t.nao}
        </p>
        {q.observacoes && (
          <p>
            {t.observacoes}: {q.observacoes}
          </p>
        )}
      </section>
      {!!dados.analogias?.length && (
        <section className="cartao">
          <h2>{t.analogias}</h2>
          {dados.analogias.map((a) => (
            <article key={a.id}>
              <h3>{a.conceito}</h3>
              <strong>{t.analogiaAviso}</strong>
              <p>{a.analogia}</p>
              <ul>
                {a.mapeamento.map((mapa, i) => (
                  <li key={i}>
                    {mapa.termo_tecnico} → {mapa.elemento_analogia}
                  </li>
                ))}
              </ul>
              <p>
                <strong>{t.limite}:</strong> {a.limite_da_analogia}
              </p>
              <small>
                {t.conceitosAncorados}: {lista(a.conceito_ancorado_em)}
              </small>
              {!!a.fontes_externas?.length && (
                <p>
                  {t.fontesExternas}: {lista(a.fontes_externas)}
                </p>
              )}
            </article>
          ))}
        </section>
      )}
      {dados.microlearning && (
        <section className="cartao">
          <h2>{t.microlearning}</h2>
          <p>
            {t.duracao}: {dados.microlearning.duracao_total_min} {t.minutos}
          </p>
          {dados.microlearning.blocos.map((b) => (
            <article key={b.ordem}>
              <h3>
                {b.ordem}. {b.titulo}
              </h3>
              <p>
                {b.duracao_min} {t.minutos} · {t.objetivo}: {b.objetivo}
              </p>
              <small>
                {t.itensRef}: {b.itens_ref.map((i) => i + 1).join(', ')}
              </small>
            </article>
          ))}
        </section>
      )}
      {trilha && (
        <section className="cartao">
          <h2>{t.evolucao}</h2>
          <p>
            {t.nivelAtual}: {textos.opcoes.niveis[trilha.nivel_atual]}
          </p>
          <p>
            {t.proximoNivel}:{' '}
            {trilha.proximo_nivel
              ? textos.opcoes.niveis[trilha.proximo_nivel]
              : t.nivelMaximo}
          </p>
          <p>
            {t.xp}: {trilha.xp_total}
          </p>
          <p>
            {t.xpSessao}: {trilha.xp_ganho_nesta_sessao}
          </p>
          <p>
            {t.xpValidacao}: {trilha.xp_disponivel_ao_validar}
          </p>
          <p>
            {t.limiarXp}: {trilha.xp_para_proximo_nivel}
          </p>
          <p>
            {t.progresso}: {trilha.progresso_percentual}%
          </p>
          <progress
            aria-label={t.progresso}
            max="100"
            value={Math.max(0, Math.min(100, trilha.progresso_percentual))}
          />
          <p>
            {t.dominados}: {lista(trilha.conceitos_dominados)}
          </p>
          <p>
            {t.aprendendo}: {lista(trilha.conceitos_em_aprendizado)}
          </p>
          <p>
            {t.teste}: {trilha.teste_nivel_disponivel ? t.sim : t.nao}
          </p>
          <p>
            {t.limiar}: {percentual(trilha.limiar_aprovacao)}
          </p>
          <p>
            {t.sugestao}: {trilha.sugestao_promocao ? t.sim : t.nao}
          </p>
        </section>
      )}

      <div className="acoes-resultado">
        {children}
        {todosRespondidos && (
          <button
            type="button"
            className="botao botao-secundario"
            onClick={reiniciarQuiz}
          >
            Refazer quiz
          </button>
        )}
      </div>
    </>
  )
}
