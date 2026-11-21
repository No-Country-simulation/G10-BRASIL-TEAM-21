import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { apiAdaptacoes } from '../api/adaptacoes'
import { apiDocumentos, type Documento } from '../api/documentos'
import { configuracao } from '../api/configuracao'
import { ErroApi } from '../api/erros'
import type { AdaptacaoRequest } from '../api/tipos'
import { EstadoTela } from '../components/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'
import { textos } from '../texts/pt-BR'

function formatoInicial(valor: string | null): AdaptacaoRequest['formato_saida'] {
  const formatos = Object.keys(textos.opcoes.formatos) as AdaptacaoRequest['formato_saida'][]
  const encontrado = formatos.find((formato) => formato === valor)
  if (!encontrado || (configuracao.usarMock && encontrado !== 'Flashcards'))
    return 'Flashcards'
  return encontrado
}

export default function Adaptacoes() {
  const [params] = useSearchParams()
  const estado = useEstadoMock()
  const navigate = useNavigate()
  const [documentos, setDocumentos] = useState<Documento[]>([])
  const [documentoId, setDocumentoId] = useState('')
  const [formato, setFormato] = useState<AdaptacaoRequest['formato_saida']>(() => formatoInicial(params.get('formato')))
  const [nivel, setNivel] = useState<AdaptacaoRequest['perfil_destinatario']>('Iniciante')
  const [nicho, setNicho] = useState<AdaptacaoRequest['nicho_setor']>('Geral')
  const [carregando, setCarregando] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<ErroApi>()
  const t = textos.upload

  useEffect(() => {
    const controller = new AbortController()
    apiDocumentos.listar(controller.signal)
      .then((itens) => {
        if (!controller.signal.aborted) {
          setDocumentos(itens)
          const solicitado = params.get('documento_id')
          setDocumentoId(itens.find((item) => item.documento_id === solicitado)?.documento_id ?? itens[0]?.documento_id ?? '')
        }
      })
      .catch((falha: unknown) => {
        if (!controller.signal.aborted)
          setErro(falha instanceof ErroApi ? falha : new ErroApi('DESCONHECIDO'))
      })
      .finally(() => { if (!controller.signal.aborted) setCarregando(false) })
    return () => controller.abort()
  }, [params])

  const estadoTela = carregando ? 'carregando' : erro && documentos.length === 0 ? 'erro' : documentos.length === 0 ? 'vazio' : estado

  return (
    <section className="pagina">
      <EstadoTela
        estado={estadoTela}
        erro={erro}
        mensagemVazia={t.semDocumentos}
        aoTentarNovamente={() => window.location.reload()}
      >
        <h1>{t.tituloAdaptacao}</h1>
        <p>{t.descricaoAdaptacao}</p>
        {!documentos.length ? (
          <Link to="/upload" className="botao botao-primario">{t.enviarArquivo}</Link>
        ) : (
          <form aria-busy={enviando} onSubmit={async (e) => {
            e.preventDefault()
            setErro(undefined)
            setEnviando(true)
            try {
              const form = new FormData(e.currentTarget)
              const payload: AdaptacaoRequest = {
                documento_id: documentoId,
                perfil_destinatario: nivel,
                formato_saida: formato,
                nicho_setor: nicho,
                nivel_detalhe: form.get('detalhe') as AdaptacaoRequest['nivel_detalhe'],
                incluir_analogias: form.has('analogias'),
                incluir_microlearning: form.has('microlearning'),
              }
              const resultado = await apiAdaptacoes.gerar(payload)
              navigate('/resultado/recente', { state: { resultado } })
            } catch (falha) {
              setErro(falha instanceof ErroApi ? falha : new ErroApi('DESCONHECIDO'))
            } finally {
              setEnviando(false)
            }
          }}>
            <label htmlFor="documento">{t.documentoExistente}</label>
            <select id="documento" value={documentoId} onChange={(e) => setDocumentoId(e.target.value)}>
              {documentos.map((documento) => <option key={documento.documento_id} value={documento.documento_id}>{documento.titulo}</option>)}
            </select>
            <label htmlFor="formato">{t.formato}</label>
            <select id="formato" value={formato} onChange={(e) => setFormato(e.target.value as typeof formato)}>
              {Object.entries(textos.opcoes.formatos).map(([valor, rotulo]) => <option key={valor} value={valor} disabled={configuracao.usarMock && valor !== 'Flashcards'}>{rotulo}</option>)}
            </select>
            <label htmlFor="nivel">{t.perfil}</label>
            <select id="nivel" value={nivel} onChange={(e) => setNivel(e.target.value as typeof nivel)}>
              {Object.entries(textos.opcoes.niveis).map(([valor, rotulo]) => <option key={valor} value={valor}>{rotulo}</option>)}
            </select>
            <label htmlFor="nicho">{t.nicho}</label>
            <select id="nicho" value={nicho} onChange={(e) => setNicho(e.target.value as typeof nicho)}>
              {Object.entries(textos.opcoes.nichos).map(([valor, rotulo]) => <option key={valor} value={valor}>{rotulo}</option>)}
            </select>
            <label htmlFor="detalhe">{t.detalhe}</label>
            <select id="detalhe" name="detalhe" defaultValue="Didatico">
              {Object.entries(textos.opcoes.detalhes).map(([valor, rotulo]) => <option key={valor} value={valor}>{rotulo}</option>)}
            </select>
            <label><input type="checkbox" name="analogias" />{t.analogias}</label>
            <label><input type="checkbox" name="microlearning" />{t.microlearning}</label>
            <button type="submit" disabled={enviando}>{enviando ? textos.estados.carregando : t.gerar}</button>
            {erro && <div role="alert"><p>{erro.message}</p>{erro.requestId && <small>{textos.estados.referencia}: {erro.requestId}</small>}</div>}
          </form>
        )}
      </EstadoTela>
    </section>
  )
}
