import { useSearchParams } from 'react-router-dom'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'

const exemplos: Record<string, { titulo: string; conteudo: string[] }> = {
  Resumo: {
    titulo: 'Resumo do conteúdo',
    conteudo: ['Conceito principal: exemplo de conteúdo adaptado.', 'Ponto importante: revise os conceitos apresentados na fonte.'],
  },
  Tutorial: {
    titulo: 'Tutorial',
    conteudo: ['Passo 1: identifique o objetivo.', 'Passo 2: aplique o procedimento descrito.', 'Passo 3: confira o resultado.'],
  },
  Flashcards: {
    titulo: 'Flashcards',
    conteudo: ['Frente: Qual é o conceito principal?', 'Verso: Consulte a explicação correspondente na fonte.'],
  },
  Quiz: {
    titulo: 'Quiz',
    conteudo: ['Pergunta: qual alternativa representa o conceito apresentado?', 'A) Alternativa de exemplo', 'B) Outra alternativa de exemplo'],
  },
  'Roteiro de Aula': {
    titulo: 'Roteiro de aula',
    conteudo: ['Bloco 1: introdução ao tema.', 'Bloco 2: explicação e discussão dos conceitos.'],
  },
}

export default function Resultado() {
  const estado = useEstadoMock()
  const [params] = useSearchParams()

  const formato = params.get('formato') ?? 'Resumo'
  const alerta_descompasso = params.get('alerta_descompasso') === 'true'
  const status_upload = params.get('status_upload') ?? 'concluido'
  const ancoragem_fonte_score = Number(params.get('ancoragem_fonte_score') ?? '0.98')
  const nivelDocumento = params.get('nivelDocumento') ?? 'Avancado'
  const nivelUsuario = params.get('nivelUsuario') ?? 'Iniciante'
  const nivelDocumentoDesconhecido = params.get('nivelDocumento') === 'null'
  const exemplo = exemplos[formato] ?? exemplos.Resumo

  return (
    <section className="pagina">
      <EstadoTela
        estado={estado}
        mensagemVazia="Ainda não há resultado de adaptação para exibir."
        mensagemErro="Não foi possível carregar o resultado da adaptação."
      >
        <>
          <h1>Resultado da adaptação</h1>
          <p>Exemplo demonstrativo de conteúdo adaptado.</p>

          {alerta_descompasso && !nivelDocumentoDesconhecido && (
            <aside className="aviso" role="status">
              <strong>Aviso de divergência de nível</strong>
              <p>Este material pode estar acima do nível selecionado.</p>
              <p>Nível do documento: {nivelDocumento} | Seu nível: {nivelUsuario}</p>
            </aside>
          )}

          {status_upload === 'pendente' || status_upload === 'falha' ? (
            <aside className="aviso" role="status">
              <strong>Aviso de armazenamento</strong>
              <p>
                {status_upload === 'pendente'
                  ? 'O armazenamento do arquivo está pendente.'
                  : 'Não foi possível concluir o armazenamento do arquivo.'}
                {' '}O conteúdo gerado continua disponível nesta demonstração.
              </p>
            </aside>
          ) : null}

          <article className="cartao">
            <h2>{exemplo.titulo}</h2>
            {exemplo.conteudo.map((item) => <p key={item}>{item}</p>)}
          </article>

          <section className="cartao">
            <h2>Qualidade e referência à fonte</h2>
            <p>
              Ancoragem na fonte:{' '}
              {Number.isFinite(ancoragem_fonte_score)
                ? `${Math.round(ancoragem_fonte_score * 100)}%`
                : 'Indisponível'}
            </p>
            <progress
              value={Number.isFinite(ancoragem_fonte_score)
                ? Math.max(0, Math.min(1, ancoragem_fonte_score))
                : 0}
              max="1"
            />
            {Number.isFinite(ancoragem_fonte_score) && ancoragem_fonte_score < 0.8 && (
              <p className="aviso">
                A pontuação está abaixo do limite de referência de 80%. Revise as observações de qualidade.
              </p>
            )}
          </section>

          <p>
            <a href="/upload">Novo conteúdo</a> · <a href="/historico">Ver histórico</a>
          </p>
        </>
      </EstadoTela>
    </section>
  )
}
