import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiAdaptacoes } from '../api/adaptacoes'
import { configuracao } from '../api/configuracao'
import { ErroApi } from '../api/erros'
import type { AdaptacaoRequest } from '../api/tipos'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'
import { textos } from '../texts/pt-BR'

export default function Upload() {
  const estado = useEstadoMock()
  const navigate = useNavigate()
  const [origem, setOrigem] = useState('texto')
  const [arquivo, setArquivo] = useState<File>()
  const [formato, setFormato] =
    useState<AdaptacaoRequest['formato_saida']>('Flashcards')
  const [nivel, setNivel] =
    useState<AdaptacaoRequest['perfil_destinatario']>('Iniciante')
  const [nicho, setNicho] = useState<AdaptacaoRequest['nicho_setor']>('Geral')
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<ErroApi>()
  const t = textos.upload

  return (
    <section className="pagina">
      <EstadoTela estado={estado} mensagemVazia={t.vazio}>
        <h1>{t.titulo}</h1>
        <p>{t.descricao}</p>
        {configuracao.usarMock && (
          <aside className="aviso">
            <p>{t.demonstracao}</p>
            <Link to="/resultado/demo-1">{t.exemplo}</Link>
          </aside>
        )}
        <form
          aria-busy={enviando}
          onSubmit={async (e) => {
            e.preventDefault()
            const form = new FormData(e.currentTarget)
            setErro(undefined)
            setEnviando(true)
            try {
              const payload: AdaptacaoRequest = {
                perfil_destinatario: nivel,
                formato_saida: formato,
                nicho_setor: nicho,
                nivel_detalhe: form.get(
                  'detalhe',
                ) as AdaptacaoRequest['nivel_detalhe'],
                incluir_analogias: form.has('analogias'),
                incluir_microlearning: form.has('microlearning'),
              }
              if (origem === 'arquivo') {
                if (!arquivo) throw new ErroApi('REQUISICAO_INVALIDA')
                if (arquivo.size > 10 * 1024 * 1024)
                  throw new ErroApi('ARQUIVO_MUITO_GRANDE')
                if (!/\.(pdf|md|txt)$/i.test(arquivo.name))
                  throw new ErroApi('FORMATO_NAO_SUPORTADO')
                payload.documento_id = (
                  await apiAdaptacoes.enviarDocumento(arquivo)
                ).documento_id
              } else {
                payload.documento_titulo = String(form.get('titulo')).trim()
                payload.documento_conteudo = String(form.get('conteudo')).trim()
                if (!payload.documento_titulo || !payload.documento_conteudo)
                  throw new ErroApi('REQUISICAO_INVALIDA')
              }
              await apiAdaptacoes.gerar(payload)
              navigate('/resultado/recente')
            } catch (falha) {
              setErro(
                falha instanceof ErroApi ? falha : new ErroApi('DESCONHECIDO'),
              )
            } finally {
              setEnviando(false)
            }
          }}
        >
          <label htmlFor="origem">{t.origem}</label>
          <select
            id="origem"
            value={origem}
            onChange={(e) => setOrigem(e.target.value)}
          >
            <option value="texto">{t.texto}</option>
            <option value="arquivo" disabled={configuracao.usarMock}>
              {t.arquivo}
            </option>
          </select>
          {origem === 'arquivo' ? (
            <>
              <label htmlFor="arquivo">{t.arquivo}</label>
              <input
                id="arquivo"
                type="file"
                accept=".pdf,.md,.txt"
                required
                onChange={(e) => setArquivo(e.target.files?.[0])}
              />
              {arquivo && (
                <p>
                  {t.arquivoSelecionado}: {arquivo.name}
                </p>
              )}
            </>
          ) : (
            <>
              <label htmlFor="titulo">{t.tituloDocumento}</label>
              <input id="titulo" name="titulo" required />
              <label htmlFor="conteudo">{t.conteudo}</label>
              <textarea id="conteudo" name="conteudo" required rows={5} />
            </>
          )}
          <label htmlFor="formato">{t.formato}</label>
          <select
            id="formato"
            value={formato}
            onChange={(e) => setFormato(e.target.value as typeof formato)}
          >
            {Object.entries(textos.opcoes.formatos).map(([valor, rotulo]) => (
              <option
                key={valor}
                value={valor}
                disabled={configuracao.usarMock && valor !== 'Flashcards'}
              >
                {rotulo}
              </option>
            ))}
          </select>
          <label htmlFor="nivel">{t.perfil}</label>
          <select
            id="nivel"
            value={nivel}
            onChange={(e) => setNivel(e.target.value as typeof nivel)}
          >
            {Object.entries(textos.opcoes.niveis).map(([valor, rotulo]) => (
              <option key={valor} value={valor}>
                {rotulo}
              </option>
            ))}
          </select>
          <label htmlFor="nicho">{t.nicho}</label>
          <select
            id="nicho"
            value={nicho}
            onChange={(e) => setNicho(e.target.value as typeof nicho)}
          >
            {Object.entries(textos.opcoes.nichos).map(([valor, rotulo]) => (
              <option key={valor} value={valor}>
                {rotulo}
              </option>
            ))}
          </select>
          <label htmlFor="detalhe">{t.detalhe}</label>
          <select id="detalhe" name="detalhe" defaultValue="Didatico">
            {Object.entries(textos.opcoes.detalhes).map(([valor, rotulo]) => (
              <option key={valor} value={valor}>
                {rotulo}
              </option>
            ))}
          </select>
          <label>
            <input type="checkbox" name="analogias" />
            {t.analogias}
          </label>
          <label>
            <input type="checkbox" name="microlearning" />
            {t.microlearning}
          </label>
          <button type="submit" disabled={enviando}>
            {enviando ? textos.estados.carregando : t.gerar}
          </button>
          {erro && (
            <div role="alert">
              <p>{erro.message}</p>
              {erro.requestId && (
                <small>
                  {textos.estados.referencia}: {erro.requestId}
                </small>
              )}
            </div>
          )}
        </form>
      </EstadoTela>
    </section>
  )
}
