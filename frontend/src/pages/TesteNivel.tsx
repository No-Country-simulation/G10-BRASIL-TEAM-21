
import { useState } from 'react'
import { obterTokenAcesso } from '../api/sessao'

interface AlternativaTeste {
  id: string
  texto: string
}

interface PerguntaTeste {
  id: string
  pergunta: string
  alternativas: AlternativaTeste[]
  conceito_ref: string
}

interface TesteNivelResponse {
  teste_id: string
  nivel_avaliado: string
  tentativa: number
  perguntas: PerguntaTeste[]
}

interface FeedbackTeste {
  pergunta_id: string
  correta: boolean
  justificativa: string
}

interface ResultadoTeste {
  percentual_dominio: number
  aprovado: boolean
  nivel_atual: string
  conceitos_fracos: string[]
  feedback: FeedbackTeste[]
}

export default function TesteNivel() {
  const [teste, setTeste] = useState<TesteNivelResponse | null>(null)
  const [respostas, setRespostas] = useState<Record<string, string>>({})
  const [resultado, setResultado] = useState<ResultadoTeste | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState('')

  async function iniciarTeste() {
    setCarregando(true)
    setErro('')

    try {
      const token = obterTokenAcesso()

      if (!token) {
        throw new Error('Sua sessão expirou. Faça login novamente.')
      }

      const resposta = await fetch('/api/v1/testes-nivel', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!resposta.ok) {
        const detalhes = await resposta.json().catch(() => null)
        throw new Error(
          detalhes?.mensagem || 'Não foi possível iniciar o teste.',
        )
      }

      const dados: TesteNivelResponse = await resposta.json()

      if (!Array.isArray(dados.perguntas)) {
        throw new Error('Formato de resposta inválido.')
      }

      setTeste(dados)
      setRespostas({})
      setResultado(null)
    } catch (error) {
      setErro(
        error instanceof Error ? error.message : 'Erro ao iniciar o teste.',
      )
    } finally {
      setCarregando(false)
    }
  }

  function selecionarResposta(perguntaId: string, alternativaId: string) {
    setRespostas((anterior) => ({
      ...anterior,
      [perguntaId]: alternativaId,
    }))
  }

  async function enviarRespostas() {
    if (!teste) return

    if (Object.keys(respostas).length !== teste.perguntas.length) {
      setErro('Responda a todas as perguntas antes de enviar.')
      return
    }

    setEnviando(true)
    setErro('')

    try {
      const token = obterTokenAcesso()

      if (!token) {
        throw new Error('Sua sessão expirou. Faça login novamente.')
      }

      const payload = {
        respostas: teste.perguntas.map((pergunta) => ({
          pergunta_id: pergunta.id,
          alternativa_escolhida: respostas[pergunta.id],
        })),
      }

      const resposta = await fetch(
        `/api/v1/testes-nivel/${teste.teste_id}/respostas`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        },
      )

      if (!resposta.ok) {
        const detalhes = await resposta.json().catch(() => null)

        throw new Error(
          detalhes?.mensagem || 'Não foi possível enviar as respostas.',
        )
      }

      const dados: ResultadoTeste = await resposta.json()
      setResultado(dados)
    } catch (error) {
      setErro(
        error instanceof Error ? error.message : 'Erro ao enviar respostas.',
      )
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="container py-4">
      <div className="card p-4 shadow-sm">
        {!teste ? (
          <>
            <h1>Teste de nível</h1>

            <p>
              Responda às questões para identificarmos seu nível atual
              de conhecimento.
            </p>

            {erro && (
              <div className="alert alert-danger" role="alert">
                {erro}
              </div>
            )}

            <button
              className="btn btn-primary"
              onClick={iniciarTeste}
              disabled={carregando}
            >
              {carregando ? 'Iniciando...' : 'Iniciar teste'}
            </button>
          </>
        ) : resultado ? (
          <>
            <h1>Resultado da avaliação</h1>

            <div className="my-3">
              <h2>{(resultado.percentual_dominio * 100).toFixed(0)}%</h2>
              <p>Domínio dos conceitos avaliados</p>
            </div>

            <div
              className={`alert ${
                resultado.aprovado ? 'alert-success' : 'alert-warning'
              }`}
              role="status"
            >
              {resultado.aprovado
                ? 'Parabéns! Você foi aprovado nesta avaliação.'
                : 'Você ainda precisa desenvolver alguns conceitos.'}
            </div>

            <h5>Nível atual: {resultado.nivel_atual}</h5>

            {resultado.conceitos_fracos.length > 0 && (
              <>
                <h5 className="mt-4">Conceitos para revisar</h5>
                <ul>
                  {resultado.conceitos_fracos.map((conceito) => (
                    <li key={conceito}>{conceito}</li>
                  ))}
                </ul>
              </>
            )}

            {resultado.feedback.length > 0 && (
            <>
                <h5 className="mt-4">Feedback por questão</h5>

                {resultado.feedback.map((item, index) => (
                <div key={item.pergunta_id} className="card p-3 mb-3">
                    <div className="d-flex justify-content-between">
                    <strong>Questão {index + 1}</strong>

                    <span
                        className={`badge ${
                        item.correta ? 'bg-success' : 'bg-danger'
                        }`}
                    >
                        {item.correta ? 'Correta' : 'Incorreta'}
                    </span>
                    </div>

                    <p className="mt-2 mb-0">{item.justificativa}</p>
                </div>
                ))}
            </>
            )}
          </>
        ) : (
          <>
            <h1>Teste de nível</h1>

            <p className="text-muted">
              Nível avaliado: {teste.nivel_avaliado}
            </p>

            <p className="text-muted">
              {Object.keys(respostas).length} de {teste.perguntas.length}{' '}
              questões respondidas
            </p>

            <div className="progress mb-4">
              <div
                className="progress-bar"
                role="progressbar"
                style={{
                  width: `${
                    (Object.keys(respostas).length /
                      teste.perguntas.length) *
                    100
                  }%`,
                }}
                aria-valuenow={Object.keys(respostas).length}
                aria-valuemin={0}
                aria-valuemax={teste.perguntas.length}
              />
            </div>

            {teste.perguntas.map((pergunta, index) => (
              <div key={pergunta.id} className="mb-4">
                <h5>
                  {index + 1}. {pergunta.pergunta}
                </h5>

                {pergunta.alternativas.map((alternativa) => (
                  <div key={alternativa.id} className="form-check mb-2">
                    <input
                      className="form-check-input"
                      type="radio"
                      name={`pergunta-${pergunta.id}`}
                      id={`pergunta-${pergunta.id}-${alternativa.id}`}
                      value={alternativa.id}
                      checked={
                        respostas[pergunta.id] === alternativa.id
                      }
                      onChange={() =>
                        selecionarResposta(pergunta.id, alternativa.id)
                      }
                    />

                    <label
                      className="form-check-label"
                      htmlFor={`pergunta-${pergunta.id}-${alternativa.id}`}
                    >
                      {alternativa.texto}
                    </label>
                  </div>
                ))}
              </div>
            ))}

            {erro && (
              <div className="alert alert-danger" role="alert">
                {erro}
              </div>
            )}

            <button
              className="btn btn-primary mt-3"
              onClick={enviarRespostas}
              disabled={
                enviando ||
                Object.keys(respostas).length !== teste.perguntas.length
              }
            >
              {enviando ? 'Enviando respostas...' : 'Enviar respostas'}
            </button>
          </>
        )}
      </div>
    </main>
  )
}
