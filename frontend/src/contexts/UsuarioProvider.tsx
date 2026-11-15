import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { ErroApi } from '../api/erros'
import { definirTokenAcesso } from '../api/sessao'
import { apiUsuario } from '../api/usuario'
import { UsuarioContext } from './usuario-context'
import type { UsuarioContexto } from './usuario-context'

/**
 * Busca os dados da conta uma única vez e compartilha com Sidebar, Header e Painel.
 * Se o token estiver expirado/inválido (401), encerra a sessão e volta ao login.
 */
export function UsuarioProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [estado, setEstado] = useState<UsuarioContexto>({
    usuario: null,
    carregando: true,
  })

  useEffect(() => {
    let ativo = true

    apiUsuario
      .obterAtual()
      .then((usuario) => {
        if (ativo) setEstado({ usuario, carregando: false })
      })
      .catch((erro: unknown) => {
        if (!ativo) return

        if (erro instanceof ErroApi && erro.status === 401) {
          definirTokenAcesso(null)
          navigate('/login', { replace: true })
          return
        }

        setEstado({ usuario: null, carregando: false })
      })

    return () => {
      ativo = false
    }
  }, [navigate])

  return (
    <UsuarioContext.Provider value={estado}>{children}</UsuarioContext.Provider>
  )
}
