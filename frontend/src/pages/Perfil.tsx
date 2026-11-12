import { useEffect, useState } from 'react'

import { EstadoTela } from '../components/EstadoTela'
import { apiUsuario } from '../api/usuario'
import type { Perfil as PerfilApi } from '../api/tipos'
import type { Estado } from '../hooks/useEstadoMock'
import type { ErroApi } from '../api/erros'
import { textos } from '../texts/pt-BR'

export default function Perfil() {
  const t = textos.perfil
  const r = textos.resultado

  const [estado, setEstado] = useState<Estado>('carregando')
  const [perfil, setPerfil] = useState<PerfilApi | null>(null)
  const [erro, setErro] = useState<ErroApi>()

  useEffect(() => {
    let ativo = true

    apiUsuario
      .obterPerfil()
      .then((dados) => {
        if (!ativo) return

        setPerfil(dados)
        setEstado('sucesso')
      })
      .catch((erroApi: ErroApi) => {
        if (!ativo) return

        setErro(erroApi)
        setEstado('erro')
      })

    return () => {
      ativo = false
    }
  }, [])

  return (
    <section className="pagina">
      <EstadoTela
        estado={estado}
        mensagemVazia={t.vazio}
        erro={erro}
        aoTentarNovamente={() => window.location.reload()}
      >
        {perfil && (
          <>
            <h1>{t.titulo}</h1>
            <p>{t.descricao}</p>

            <article className="cartao">
              <h2>
                {r.nivelAtual}:{' '}
                {textos.opcoes.niveis[perfil.nivel_atual]}
              </h2>

              <p>
                {r.proximoNivel}:{' '}
                {perfil.proximo_nivel
                  ? textos.opcoes.niveis[perfil.proximo_nivel]
                  : r.nivelMaximo}
              </p>

              <p>
                {r.xp}: {perfil.xp_total}
              </p>

              <p>
                {r.limiarXp}: {perfil.xp_para_proximo_nivel}
              </p>

              <label htmlFor="progresso">
                {r.progresso}: {perfil.progresso_percentual}%
              </label>

              <progress
                id="progresso"
                value={perfil.progresso_percentual}
                max="100"
              />
            </article>

            <article className="cartao">
              <h2>{t.conhecimentos}</h2>

              <h3>{r.dominados}</h3>
              {perfil.conceitos_dominados.length > 0 ? (
                <ul>
                  {perfil.conceitos_dominados.map((conceito) => (
                    <li key={conceito}>{conceito}</li>
                  ))}
                </ul>
              ) : (
                <p>{r.nenhum}</p>
              )}

              <h3>{r.aprendendo}</h3>
              {perfil.conceitos_em_aprendizado.length > 0 ? (
                <ul>
                  {perfil.conceitos_em_aprendizado.map((conceito) => (
                    <li key={conceito}>{conceito}</li>
                  ))}
                </ul>
              ) : (
                <p>{r.nenhum}</p>
              )}
            </article>

            <article className="cartao">
              <h2>{t.avaliacao}</h2>

              <p>
                {r.limiar}: {perfil.limiar_aprovacao}%
              </p>

              {perfil.sugestao_promocao && <p>{r.sugestao}</p>}

              <button
                type="button"
                disabled={!perfil.teste_nivel_disponivel}
              >
                {t.fazerTeste}
              </button>

              {!perfil.teste_nivel_disponivel && (
                <p>{t.testeIndisponivel}</p>
              )}
            </article>
          </>
        )}
      </EstadoTela>
    </section>
  )
}