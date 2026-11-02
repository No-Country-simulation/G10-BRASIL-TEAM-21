import type { Adaptacao, ItemConteudo } from '../api/tipos'
import { textos } from '../texts/pt-BR'

const t = textos.resultado
const percentual = (valor: number) =>
  `${Math.round(Math.max(0, Math.min(1, valor)) * 100)}%`
const lista = (itens: string[]) => itens.join(', ') || t.nenhum

function ItemAdaptado({ item }: { item: ItemConteudo }) {
  return (
    <article className="cartao">
      {'frente' in item && (
        <>
          <h2>{item.frente}</h2>
          <p>{item.verso}</p>
          <p>
            <strong>{t.dica}:</strong> {item.dica_didatica}
          </p>
        </>
      )}
      {'pergunta' in item && (
        <>
          <h2>{item.pergunta}</h2>
          <ul>
            {item.alternativas.map((a) => (
              <li key={a.id}>
                {a.id}) {a.texto}
              </li>
            ))}
          </ul>
          <p>{t.quiz}</p>
        </>
      )}
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
      {'analogia_ref' in item && item.analogia_ref && (
        <small>
          {t.analogiaRef}: {item.analogia_ref}
        </small>
      )}
      <small>
        {t.fontes}: {lista(item.fontes_chunks)}
      </small>
    </article>
  )
}

export function PacoteAdaptacao({ dados }: { dados: Adaptacao }) {
  const m = dados.metadados
  const q = dados.avaliacao_qualidade
  const trilha = dados.trilha_evolucao
  const status = dados.armazenamento_oci.status_upload
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
        {dados.conteudo_adaptado.itens.map((item, i) => (
          <ItemAdaptado key={i} item={item} />
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
    </>
  )
}
