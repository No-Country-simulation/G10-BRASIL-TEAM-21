// @vitest-environment node
import { readFileSync } from 'node:fs'
import Ajv from 'ajv/dist/2020.js'
import addFormats from 'ajv-formats'
import { describe, expect, it } from 'vitest'
import { montarExemplo } from '../src/api/mock'
import fixture from '../mocks/adaptacao-flashcards.json'
import copia from '../src/mocks/adaptacao-flashcards.json'
import { textos } from '../src/texts/pt-BR'

const contrato = readFileSync(
  new URL('../../docs/05 - Contrato de API.md', import.meta.url),
  'utf8',
)
const openapi = JSON.parse(
  readFileSync(
    new URL('../../backend/docs/openapi.json', import.meta.url),
    'utf8',
  ),
)
const ajv = new Ajv({ strict: false, allErrors: true })
addFormats(ajv)
ajv.addSchema({ $id: 'contrato', components: openapi.components })
const validar = ajv.compile({
  $ref: 'contrato#/components/schemas/AdaptacaoResponse',
})

describe('fixtures e contrato publicado', () => {
  it('reproduz integralmente o exemplo Flashcards e mantém a cópia sincronizada', () => {
    const secao = contrato.split('### 5.2')[1].split('### 5.3')[0]
    const json = secao.match(/```json\s*([\s\S]*?)```/)?.[1]
    expect(json).toBeDefined()
    expect(fixture).toEqual(JSON.parse(json!.replace(/\u00a0/g, ' ')))
    expect(copia).toEqual(fixture)
  })
  it.each(['completo', 'nulos', 'vazio', 'pendente', 'falha'] as const)(
    'valida cenário %s no schema do backend',
    (cenario) => {
      expect(
        validar(montarExemplo({ cenario })),
        JSON.stringify(validar.errors),
      ).toBe(true)
    },
  )
  it('detecta fixture com enum inválido', () => {
    const dados = structuredClone(fixture)
    dados.metadados.formato_gerado = 'formato inexistente'
    expect(validar(dados)).toBe(false)
  })
  it('cobre todos os códigos da seção 8 com mensagens centralizadas', () => {
    const secao = contrato.split('## 8. Erros')[1].split('## 9.')[0]
    const codigos = [...secao.matchAll(/\| \d{3} \| `([A-Z_]+)`/g)].map(
      (m) => m[1],
    )
    expect(codigos).toHaveLength(18)
    for (const codigo of codigos) expect(textos.erros).toHaveProperty(codigo)
  })
})
