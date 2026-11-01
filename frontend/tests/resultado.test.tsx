import { StrictMode } from 'react'
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import App from '../src/App'
import { PacoteAdaptacao } from '../src/componentes/PacoteAdaptacao'
import { montarExemplo } from '../src/api/mock'
import { textos } from '../src/texts/pt-BR'
import { apiAdaptacoes } from '../src/api/adaptacoes'
import { ErroApi } from '../src/api/erros'

const { config } = vi.hoisted(() => ({
  config: { usarMock: true, url: '/api/v1' },
}))
vi.mock('../src/api/configuracao', () => ({ configuracao: config }))
afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})
beforeEach(() => {
  config.usarMock = true
})

function abrir(url: string) {
  return render(
    <StrictMode>
      <MemoryRouter initialEntries={[url]}>
        <App />
      </MemoryRouter>
    </StrictMode>,
  )
}

describe('resultado do contrato', () => {
  it('gera a demonstração pelo formulário e navega até o pacote recebido', async () => {
    abrir('/upload')
    fireEvent.change(screen.getByLabelText(textos.upload.tituloDocumento), { target: { value: 'Documento de teste' } })
    fireEvent.change(screen.getByLabelText(textos.upload.conteudo), { target: { value: 'Texto para adaptar' } })
    fireEvent.click(screen.getByRole('button', { name: textos.upload.gerar }))
    expect(screen.getByRole('button', { name: textos.estados.carregando }).hasAttribute('disabled')).toBe(true)
    await screen.findByRole('heading', { name: 'Dominando Redes na Nuvem (VCN) do Zero' })
    expect(screen.getByRole('heading', { name: textos.resultado.qualidade })).toBeTruthy()
  })

  it('exibe todos os blocos do exemplo completo', () => {
    render(<PacoteAdaptacao dados={montarExemplo()} />)
    for (const texto of [
      textos.resultado.analogias,
      textos.resultado.microlearning,
      textos.resultado.evolucao,
      textos.resultado.qualidade,
    ]) {
      expect(screen.getByRole('heading', { name: texto })).toBeTruthy()
    }
    expect(screen.getByText('98%')).toBeTruthy()
    expect(screen.getByText(/chunk-001, chunk-002/)).toBeTruthy()
    expect(screen.getByText(textos.resultado.analogiaAviso)).toBeTruthy()
  })
  it('tolera null e opcionais ausentes sem apagar os Flashcards', () => {
    const dados = montarExemplo({ cenario: 'nulos' })
    delete dados.analogias
    render(<PacoteAdaptacao dados={dados} />)
    expect(
      screen.getByRole('heading', { name: 'O que e uma VCN na Oracle Cloud?' }),
    ).toBeTruthy()
    expect(
      screen.queryByRole('heading', { name: textos.resultado.evolucao }),
    ).toBeNull()
    expect(screen.queryByText(textos.resultado.descompasso)).toBeNull()
    expect(screen.getByText(textos.resultado.desconhecido)).toBeTruthy()
  })
  it.each(['pendente', 'falha'] as const)(
    'upload %s é aviso com conteúdo acessível',
    (cenario) => {
      render(<PacoteAdaptacao dados={montarExemplo({ cenario })} />)
      expect(screen.getByText(textos.resultado[cenario])).toBeTruthy()
      expect(screen.queryByRole('alert')).toBeNull()
      expect(
        screen.getByRole('heading', {
          name: 'O que e uma VCN na Oracle Cloud?',
        }),
      ).toBeTruthy()
    },
  )
  it('passa por carregamento e permite alternar para vazio e erro', async () => {
    abrir('/resultado/demo-1')
    expect(screen.getByText(textos.estados.carregando)).toBeTruthy()
    await screen.findByRole('heading', {
      name: 'Dominando Redes na Nuvem (VCN) do Zero',
    })
    fireEvent.change(screen.getByLabelText(textos.mock.titulo), {
      target: { value: 'vazio' },
    })
    await screen.findByText(textos.resultado.vazio)
    fireEvent.change(screen.getByLabelText(textos.mock.codigo), {
      target: { value: 'TOKEN_EXPIRADO' },
    })
    await screen.findByText(textos.erros.TOKEN_EXPIRADO)
    expect(screen.getByRole('alert')).toBeTruthy()
  })
  it('descarta requisição anterior ao trocar de cenário', async () => {
    abrir('/resultado/demo-1?cenario=carregando')
    fireEvent.change(screen.getByLabelText(textos.mock.titulo), {
      target: { value: 'nulos' },
    })
    await screen.findByText(textos.resultado.desconhecido)
    expect(screen.queryByText(textos.estados.carregando)).toBeNull()
  })
  it('modo real ignora simulações da URL e mostra 501 com nova tentativa', async () => {
    config.usarMock = false
    const obter = vi
      .spyOn(apiAdaptacoes, 'obter')
      .mockRejectedValue(new ErroApi('NAO_IMPLEMENTADO', 501))
    abrir('/resultado/id-real?cenario=vazio&estado=erro')
    await screen.findByText(textos.erros.NAO_IMPLEMENTADO)
    expect(screen.queryByLabelText(textos.mock.titulo)).toBeNull()
    const chamadas = obter.mock.calls.length
    fireEvent.click(screen.getByRole('button', { name: textos.estados.tentar }))
    await waitFor(() =>
      expect(obter.mock.calls.length).toBeGreaterThan(chamadas),
    )
  })
})
