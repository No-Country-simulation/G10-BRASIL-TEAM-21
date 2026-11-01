// @vitest-environment node
import { afterEach, describe, expect, it, vi } from 'vitest'
import { criarApiAdaptacoes } from '../src/api/adaptacoes'
import { criarClienteHttp } from '../src/api/cliente'
import { lerConfiguracao } from '../src/api/configuracao'
import { ErroApi, normalizarErro } from '../src/api/erros'
import { obterMock } from '../src/api/mock'
import { textos } from '../src/texts/pt-BR'

const config = { usarMock: false, url: 'https://api.exemplo/api/v1' }
afterEach(() => vi.useRealTimers())

describe('cliente de API', () => {
  it('interpreta true/false explicitamente e normaliza a URL', () => {
    expect(
      lerConfiguracao({ VITE_USE_MOCK: 'false', VITE_API_URL: '/api/v1/' }),
    ).toEqual({ usarMock: false, url: '/api/v1' })
    expect(lerConfiguracao({ VITE_USE_MOCK: 'true' }).usarMock).toBe(true)
    expect(lerConfiguracao({}).usarMock).toBe(false)
  })
  it('modo mock carrega JSON sem fazer chamada de rede', async () => {
    const rede = vi.fn<typeof fetch>()
    const api = criarApiAdaptacoes(
      { ...config, usarMock: true },
      () => null,
      rede,
    )
    const dados = await api.obter('demo-1')
    expect(dados.conteudo_adaptado.itens[0]).toHaveProperty('frente')
    expect(rede).not.toHaveBeenCalled()
  })
  it('modo real usa URL configurada, identificador opaco e Bearer', async () => {
    const rede = vi
      .fn<typeof fetch>()
      .mockResolvedValue(Response.json({ conteudo: 'real' }))
    await criarApiAdaptacoes(config, () => 'token-apenas-no-teste', rede).obter(
      'id /?#',
    )
    expect(rede.mock.calls[0][0]).toBe(
      'https://api.exemplo/api/v1/adaptacoes/id%20%2F%3F%23',
    )
    expect(
      new Headers(rede.mock.calls[0][1]?.headers).get('Authorization'),
    ).toBe('Bearer token-apenas-no-teste')
  })
  it('mantém 501 do backend, sem trocar por mock', async () => {
    const rede = vi
      .fn<typeof fetch>()
      .mockResolvedValue(
        Response.json(
          { codigo: 'NAO_IMPLEMENTADO', request_id: 'req-real' },
          { status: 501 },
        ),
      )
    await expect(
      criarApiAdaptacoes(config, () => null, rede).obter('real', undefined, {
        cenario: 'completo',
      }),
    ).rejects.toMatchObject({
      status: 501,
      message: textos.erros.NAO_IMPLEMENTADO,
      requestId: 'req-real',
    })
    expect(rede).toHaveBeenCalledTimes(1)
  })
  it('envia JSON e não força Content-Type em FormData', async () => {
    const rede = vi
      .fn<typeof fetch>()
      .mockImplementation(async () => Response.json({ ok: true }))
    const cliente = criarClienteHttp(config, () => null, rede)
    await cliente('/adaptacoes', {
      method: 'POST',
      body: JSON.stringify({ documento_id: 'doc' }),
    })
    expect(
      new Headers(rede.mock.calls[0][1]?.headers).get('Content-Type'),
    ).toBe('application/json')
    await cliente('/documentos', { method: 'POST', body: new FormData() })
    expect(
      new Headers(rede.mock.calls[1][1]?.headers).has('Content-Type'),
    ).toBe(false)
  })
  it('aceita 204 sem tentar interpretar JSON', async () => {
    const rede = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(null, { status: 204 }))
    await expect(
      criarClienteHttp(config, () => null, rede)('/auth/logout'),
    ).resolves.toBeUndefined()
  })
  it('normaliza falha de conexão e resposta não JSON', async () => {
    const rede = vi
      .fn<typeof fetch>()
      .mockRejectedValueOnce(new TypeError('network'))
      .mockResolvedValueOnce(new Response('<html>erro</html>'))
    const cliente = criarClienteHttp(config, () => null, rede)
    await expect(cliente('/adaptacoes')).rejects.toMatchObject({
      codigo: 'CONEXAO_INDISPONIVEL',
    })
    await expect(cliente('/adaptacoes')).rejects.toMatchObject({
      codigo: 'RESPOSTA_INVALIDA',
    })
  })
  it('preserva cancelamento HTTP e cancela cenário mock de carregamento', async () => {
    const rede = vi
      .fn<typeof fetch>()
      .mockRejectedValue(new DOMException('Aborted', 'AbortError'))
    await expect(
      criarClienteHttp(config, () => null, rede)('/adaptacoes'),
    ).rejects.toMatchObject({ name: 'AbortError' })
    const controller = new AbortController()
    const promessa = obterMock({ cenario: 'carregando' }, controller.signal)
    controller.abort()
    await expect(promessa).rejects.toMatchObject({ name: 'AbortError' })
  })
  it('não expõe mensagens técnicas desconhecidas e preserva dados para suporte', () => {
    const erro = normalizarErro(
      {
        codigo: 'NOVO_CODIGO',
        mensagem: 'Stack trace interno',
        request_id: 'req-x',
        detalhes: [{ campo: 'email', mensagem: 'inválido' }, null],
      },
      422,
    )
    expect(erro.message).toBe(textos.erros.DESCONHECIDO)
    expect(erro.requestId).toBe('req-x')
    expect(erro.detalhes).toEqual([{ campo: 'email', mensagem: 'inválido' }])
    expect(normalizarErro({ codigo: 'EMAIL_EXISTE' }, 400).codigo).toBe(
      'EMAIL_JA_CADASTRADO',
    )
    expect(new ErroApi('TOKEN_EXPIRADO').message).toBe(
      textos.erros.TOKEN_EXPIRADO,
    )
  })
})
