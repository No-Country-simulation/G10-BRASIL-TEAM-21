import { Link } from 'react-router-dom'
import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'
import { textos } from '../texts/pt-BR'

export default function Historico() {
  const estado = useEstadoMock()
  const t = textos.historico
  return (
    <section className="pagina">
      <EstadoTela estado={estado} mensagemVazia={t.vazio}>
        <h1>{t.titulo}</h1>
        <p>{t.descricao}</p>
        <p>{t.previa}</p>
        <article className="cartao">
          <h2>{textos.opcoes.formatos.Flashcards}</h2>
          <p>
            {textos.resultado.perfil}: {textos.opcoes.niveis.Iniciante}
          </p>
          <Link to="/resultado/demo-1">{t.abrir}</Link>
        </article>
      </EstadoTela>
    </section>
  )
}
