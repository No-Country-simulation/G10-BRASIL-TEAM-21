import { Link } from 'react-router-dom'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'

const adaptacoes = [
  { id: 'demo-1', titulo: 'Introdução ao tema', perfil: 'Iniciante', formato: 'Resumo', score: 0.98, status: 'concluido', data: '28/10/2026' },
  { id: 'demo-2', titulo: 'Conceitos fundamentais', perfil: 'Intermediario', formato: 'Flashcards', score: 0.86, status: 'pendente', data: '27/10/2026' },
]

export default function Historico() {
  const estado = useEstadoMock()

  return (
    <section className="pagina">
      <EstadoTela
        estado={estado}
        mensagemVazia="Você ainda não gerou nenhum conteúdo."
        mensagemErro="Não foi possível carregar o histórico de adaptações."
      >
        <>
          <h1>Histórico de adaptações</h1>
          <p>Consulte os conteúdos gerados anteriormente.</p>

          <div className="lista-cartoes">
            {adaptacoes.map((item) => (
              <article className="cartao" key={item.id}>
                <h2>{item.titulo}</h2>
                <p>Formato: {item.formato}</p>
                <p>Perfil aplicado: {item.perfil}</p>
                <p>Ancoragem na fonte: {Math.round(item.score * 100)}%</p>
                <p>Status do armazenamento: {item.status}</p>
                <p>Data: {item.data}</p>
                <Link to={`/resultado/${item.id}`}>Abrir resultado demonstrativo</Link>
              </article>
            ))}
          </div>
        </>
      </EstadoTela>
    </section>
  )
}
