import { EstadoTela } from '../componentes/EstadoTela'
import { useEstadoMock } from '../hooks/useEstadoMock'

export default function Perfil() {
  const estado = useEstadoMock()
  const testeDisponivel = true
  const progresso = 65

  return (
    <section className="pagina">
      <EstadoTela
        estado={estado}
        mensagemVazia="Ainda não há informações de perfil e evolução disponíveis."
        mensagemErro="Não foi possível carregar o perfil."
      >
        <>
          <h1>Meu perfil</h1>
          <p>Acompanhe seu nível de conhecimento e sua evolução.</p>

          <article className="cartao">
            <h2>Nível atual: Intermediario</h2>
            <p>Próximo nível: Avancado</p>
            <p>XP total: 650</p>
            <p>XP para o próximo nível: 350</p>
            <label htmlFor="progresso">Progresso para o próximo nível: {progresso}%</label>
            <progress id="progresso" value={progresso} max="100" />
          </article>

          <article className="cartao">
            <h2>Conhecimentos</h2>
            <p>Conceitos dominados: fundamentos, vocabulário e conceitos básicos.</p>
            <p>Em aprendizado: aplicação prática e resolução de problemas.</p>
          </article>

          <article className="cartao">
            <h2>Avaliação de nível</h2>
            <p>Limite de aprovação: 70%</p>
            <button type="button" disabled={!testeDisponivel}>
              Fazer teste de nível
            </button>
            {!testeDisponivel && <p>O teste de nível não está disponível no momento.</p>}
          </article>
        </>
      </EstadoTela>
    </section>
  )
}
