/** Primeiro nome para saudações */
export function primeiroNome(nome?: string | null): string {
  return nome?.trim().split(/\s+/)[0] ?? ''
}

/** Iniciais para o avatar */
export function iniciais(nome?: string | null): string {
  const partes = nome?.trim().split(/\s+/).filter(Boolean) ?? []

  if (partes.length === 0) return '·'
  if (partes.length === 1) return partes[0][0].toUpperCase()

  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
}
