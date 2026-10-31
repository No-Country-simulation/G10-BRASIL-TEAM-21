import { useState } from 'react'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'

const formatos = ['Tutorial', 'Flashcards', 'Quiz', 'Resumo', 'Roteiro de Aula']
const niveis = ['Iniciante', 'Basico', 'Intermediario', 'Avancado', 'Especialista', 'Gestor/Executivo']
const nichos = ['Geral', 'Fintech', 'Saude', 'E-commerce', 'Educacao', 'Juridico']

export default function Upload() {
  const estado = useEstadoMock()
  const [arquivo, setArquivo] = useState('')
  const [formato, setFormato] = useState('Resumo')
  const [nivel, setNivel] = useState('Iniciante')
  const [nicho, setNicho] = useState('Geral')
  const [mensagem, setMensagem] = useState('')

  return (
    <section className="pagina">
      <EstadoTela
        estado={estado}
        mensagemVazia="Selecione um arquivo e configure os parâmetros para iniciar uma adaptação."
        mensagemErro="Não foi possível carregar o formulário de envio."
      >
        <>
          <h1>Novo conteúdo</h1>
          <p>Envie um material e escolha como deseja adaptá-lo.</p>

          <form onSubmit={(e) => {
            e.preventDefault()
            setMensagem('Wireframe: solicitação simulada. A integração com a API será implementada posteriormente.')
          }}>
            <label htmlFor="arquivo">Arquivo (PDF, MD ou TXT)</label>
            <input
              id="arquivo"
              type="file"
              accept=".pdf,.md,.txt"
              onChange={(e) => setArquivo(e.target.files?.[0]?.name ?? '')}
            />
            {arquivo && <p>Arquivo selecionado: {arquivo}</p>}

            <label htmlFor="formato">Formato de saída</label>
            <select id="formato" value={formato} onChange={(e) => setFormato(e.target.value)}>
              {formatos.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>

            <label htmlFor="nivel">Perfil de destino</label>
            <select id="nivel" value={nivel} onChange={(e) => setNivel(e.target.value)}>
              {niveis.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>

            <label htmlFor="nicho">Área de conhecimento</label>
            <select id="nicho" value={nicho} onChange={(e) => setNicho(e.target.value)}>
              {nichos.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>

            <label htmlFor="detalhe">Nível de detalhe</label>
            <select id="detalhe" defaultValue="Didatico">
              <option value="Didatico">Didatico</option>
              <option value="Intermediario">Intermediario</option>
              <option value="Aprofundado">Aprofundado</option>
            </select>

            <label><input type="checkbox" /> Incluir analogias</label>
            <label><input type="checkbox" /> Incluir microlearning</label>

            <button type="submit">Gerar adaptação</button>
          </form>

          {mensagem && <p role="status">{mensagem}</p>}
        </>
      </EstadoTela>
    </section>
  )
}
