export const configuracaoDemo = {
  habilitado: import.meta.env.VITE_DEMO_ENABLED === 'true',
  email: import.meta.env.VITE_DEMO_EMAIL ?? '',
  senha: import.meta.env.VITE_DEMO_PASSWORD ?? '',
}