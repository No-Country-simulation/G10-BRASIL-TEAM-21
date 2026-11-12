
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiAdaptacoes } from '../api/adaptacoes'
import type { AdaptacoesListResponse } from '../api/tipos'
import { ErroApi } from '../api/erros'
import { EstadoTela } from '../components/EstadoTela'
import { textos } from '../texts/pt-BR'

export default function Historico() {
  const t = textos.historico

  const [adaptacoes, setAdaptacoes] = useState<AdaptacoesListResponse['itens']>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<ErroApi>()
  const [tentativa, setTentativa] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function carregarHistorico() {
      setCarregando(true)
      setErro(undefined)

      try {
        const dados = await apiAdaptacoes.listar(
          100,
          0,
          controller.signal,
        )

        if (!controller.signal.aborted) {
          setAdaptacoes(dados.itens)
        }
      } catch (erro: unknown) {
        if (!controller.signal.aborted) {
          setErro(
            erro instanceof ErroApi
              ? erro
              : new ErroApi('RESPOSTA_INVALIDA'),
          )
        }
      } finally {
        if (!controller.signal.aborted) {
          setCarregando(false)
        }
      }
    }

    void carregarHistorico()

    return () => controller.abort()
  }, [tentativa])

  const estado = carregando
    ? 'carregando'
    : erro
      ? 'erro'
      : adaptacoes.length === 0
        ? 'vazio'
        : 'sucesso'

  return (
    <section className="pagina">
      <EstadoTela
        estado={estado}
        erro={erro}
        mensagemVazia={t.vazio}
        aoTentarNovamente={() => setTentativa((atual) => atual + 1)}
      >
        <h1>{t.titulo}</h1>
        <p>{t.descricao}</p>

        <div className="lista-documentos">
          {adaptacoes.map((adaptacao) => (
            <article className="cartao" key={adaptacao.adaptacao_id}>
              <h2>{adaptacao.titulo}</h2>

              <p>Formato: {adaptacao.formato_gerado}</p>
              <p>Status: {adaptacao.status_upload}</p>

              <p>
                Enviado em:{' '}
                {new Date(adaptacao.criado_em).toLocaleDateString('pt-BR')}
              </p>

              <Link
                to={`/resultado/${adaptacao.adaptacao_id}`}
                className="botao botao-primario"
              >
                Ver resultado
              </Link>
            </article>
          ))}
        </div>
      </EstadoTela>

      <div className="acoes-resultado esquerda">
        <Link to="/upload" className="botao botao-primario">
          {textos.navegacao.upload}
        </Link>
      </div>
    </section>
  )
}
