import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { apiAdaptacoes } from '../api/adaptacoes'
import { configuracao } from '../api/configuracao'
import { ErroApi } from '../api/erros'
import type { CenarioMock } from '../api/mock'
import type { Adaptacao } from '../api/tipos'
import { EstadoTela } from '../componentes/EstadoTela'
import { PacoteAdaptacao } from '../componentes/PacoteAdaptacao'
import { textos } from '../texts/pt-BR'

const cenarios = [
  'completo',
  'nulos',
  'vazio',
  'erro',
  'carregando',
  'pendente',
  'falha',
] as const

export default function Resultado() {
  const { id = 'demo-1' } = useParams()
  const [params, setParams] = useSearchParams()
  const cenario = params.get('cenario') ?? params.get('estado') ?? 'completo'
  const codigo = params.get('codigo') ?? 'BANCO_INDISPONIVEL'
  const [tentativa, setTentativa] = useState(0)
  const chave = `${id}|${configuracao.usarMock ? `${cenario}|${codigo}` : ''}|${tentativa}`
  const [resposta, setResposta] = useState<{
    chave: string
    dados?: Adaptacao
    erro?: ErroApi
  }>()

  useEffect(() => {
    const controller = new AbortController()
    const opcoes = {
      cenario: cenarios.includes(cenario as CenarioMock)
        ? (cenario as CenarioMock)
        : ('completo' as const),
      codigo,
    }
    apiAdaptacoes.obter(id, controller.signal, opcoes).then(
      (dados) => {
        if (!controller.signal.aborted) setResposta({ chave, dados })
      },
      (erro: unknown) => {
        if (!controller.signal.aborted)
          setResposta({
            chave,
            erro:
              erro instanceof ErroApi ? erro : new ErroApi('RESPOSTA_INVALIDA'),
          })
      },
    )
    return () => controller.abort()
  }, [id, chave, cenario, codigo])

  const atual = resposta?.chave === chave ? resposta : undefined
  const estado = !atual
    ? 'carregando'
    : atual.erro
      ? 'erro'
      : !atual.dados?.conteudo_adaptado.itens.length
        ? 'vazio'
        : 'sucesso'
  return (
    <section className="pagina">
      {configuracao.usarMock && (
        <fieldset className="cenarios">
          <legend>{textos.mock.titulo}</legend>
          <label htmlFor="cenario">{textos.mock.titulo}</label>
          <select
            id="cenario"
            value={
              cenarios.includes(cenario as CenarioMock) ? cenario : 'completo'
            }
            onChange={(e) => {
              const next = new URLSearchParams(params)
              next.set('cenario', e.target.value)
              next.delete('estado')
              setParams(next)
            }}
          >
            {cenarios.map((c) => (
              <option key={c} value={c}>
                {textos.mock[c]}
              </option>
            ))}
          </select>
          <label htmlFor="codigo">{textos.mock.codigo}</label>
          <select
            id="codigo"
            value={codigo}
            onChange={(e) => {
              const next = new URLSearchParams(params)
              next.set('codigo', e.target.value)
              next.set('cenario', 'erro')
              setParams(next)
            }}
          >
            {Object.keys(textos.erros).map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </fieldset>
      )}
      <EstadoTela
        estado={estado}
        erro={atual?.erro}
        mensagemVazia={textos.resultado.vazio}
        aoTentarNovamente={() => setTentativa((n) => n + 1)}
      >
        {atual?.dados && <PacoteAdaptacao dados={atual.dados} />}
      </EstadoTela>
      <p>
        <Link to="/upload">{textos.navegacao.upload}</Link> ·{' '}
        <Link to="/historico">{textos.navegacao.historico}</Link>
      </p>
    </section>
  )
}
