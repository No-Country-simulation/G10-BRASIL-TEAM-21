import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiAdaptacoes } from '../api/adaptacoes'
import { ErroApi } from '../api/erros'
import { EstadoTela } from '../components/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'
import { textos } from '../texts/pt-BR'

export default function Upload() {
  const estado = useEstadoMock()
  const navigate = useNavigate()
  const [arquivo, setArquivo] = useState<File>()
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<ErroApi>()
  const t = textos.upload

  return (
    <section className="pagina">
      <EstadoTela estado={estado} mensagemVazia={t.vazio}>
        <h1>{t.titulo}</h1>
        <p>{t.descricaoUpload}</p>
        <form aria-busy={enviando} onSubmit={async (e) => {
          e.preventDefault()
          setErro(undefined)
          setEnviando(true)
          try {
            if (!arquivo) throw new ErroApi('REQUISICAO_INVALIDA')
            if (arquivo.size > 10 * 1024 * 1024) throw new ErroApi('ARQUIVO_MUITO_GRANDE')
            if (!/\.(pdf|md|txt)$/i.test(arquivo.name)) throw new ErroApi('FORMATO_NAO_SUPORTADO')
            const documento = await apiAdaptacoes.enviarDocumento(arquivo)
            navigate(`/adaptacoes?documento_id=${encodeURIComponent(documento.documento_id)}`)
          } catch (falha) {
            setErro(falha instanceof ErroApi ? falha : new ErroApi('DESCONHECIDO'))
          } finally {
            setEnviando(false)
          }
        }}>
          <label htmlFor="arquivo">{t.arquivo}</label>
          <input className="seletor-arquivo" id="arquivo" type="file" accept=".pdf,.md,.txt" required onChange={(e) => setArquivo(e.target.files?.[0])} />
          {arquivo && <p>{t.arquivoSelecionado}: {arquivo.name}</p>}
          <button type="submit" disabled={enviando}>{enviando ? textos.estados.carregando : t.enviarArquivo}</button>
          <Link className="link-gerar-adaptacao" to="/adaptacoes">{t.irParaAdaptacoes}</Link>
          {erro && <div role="alert"><p>{erro.message}</p>{erro.requestId && <small>{textos.estados.referencia}: {erro.requestId}</small>}</div>}
        </form>
      </EstadoTela>
    </section>
  )
}
