import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'
import { textos } from '../texts/pt-BR'

export default function Perfil() {
  const estado = useEstadoMock()
  const t = textos.perfil
  const r = textos.resultado
  return (
    <section className="pagina">
      <EstadoTela estado={estado} mensagemVazia={t.vazio}>
        <h1>{t.titulo}</h1>
        <p>{t.descricao}</p>
        <p>{t.previa}</p>
        <article className="cartao">
          <h2>
            {r.nivelAtual}: {textos.opcoes.niveis.Iniciante}
          </h2>
          <p>
            {r.proximoNivel}: {textos.opcoes.niveis.Basico}
          </p>
          <p>{r.xp}: 60</p>
          <p>{r.limiarXp}: 100</p>
          <label htmlFor="progresso">{r.progresso}: 60%</label>
          <progress id="progresso" value="60" max="100" />
        </article>
        <article className="cartao">
          <h2>{t.avaliacao}</h2>
          <p>{r.limiar}: 70%</p>
          <button type="button" disabled>
            {t.fazerTeste}
          </button>
          <p>{t.testeIndisponivel}</p>
        </article>
      </EstadoTela>
    </section>
  )
}
