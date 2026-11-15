import { createContext, useContext } from 'react'
import type { Usuario } from '../api/tipos'

export interface UsuarioContexto {
  usuario: Usuario | null
  carregando: boolean
}

export const UsuarioContext = createContext<UsuarioContexto>({
  usuario: null,
  carregando: true,
})

export function useUsuario(): UsuarioContexto {
  return useContext(UsuarioContext)
}
