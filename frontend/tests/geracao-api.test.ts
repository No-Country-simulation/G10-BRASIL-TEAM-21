// @vitest-environment node
import { execFileSync } from 'node:child_process'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { afterEach, describe, expect, it } from 'vitest'

const frontend = fileURLToPath(new URL('../', import.meta.url))
const gerador = join(frontend, 'node_modules/openapi-typescript/bin/cli.js')
const verificador = join(frontend, 'scripts/verificar-api.mjs')
const publicado = readFileSync(
  new URL('../../backend/docs/openapi.json', import.meta.url),
  'utf8',
)
const pastas: string[] = []

function preparar() {
  const pasta = mkdtempSync(join(tmpdir(), 'adaptai-t6-teste-'))
  pastas.push(pasta)
  const origem = join(pasta, 'openapi.json')
  const destino = join(pasta, 'schema.d.ts')
  writeFileSync(origem, publicado)
  writeFileSync(destino, readFileSync(join(frontend, 'src/api/schema.d.ts')))
  return { origem, destino }
}

function verificar(origem: string, destino: string) {
  return execFileSync(
    process.execPath,
    [verificador, '--source', origem, '--output', destino],
    { encoding: 'utf8', stdio: 'pipe' },
  )
}

afterEach(() => {
  for (const pasta of pastas.splice(0)) {
    rmSync(pasta, { recursive: true, force: true })
  }
})

describe('sincronização dos tipos OpenAPI (T6)', () => {
  it('confirma o contrato atual sem escrever no arquivo verificado', () => {
    const { origem, destino } = preparar()
    const antes = readFileSync(destino, 'utf8')
    expect(verificar(origem, destino)).toContain('sincronizados')
    expect(readFileSync(destino, 'utf8')).toBe(antes)
  })

  it('rejeita mudança no contrato, preserva o arquivo e passa após regeneração', () => {
    const { origem, destino } = preparar()
    const contrato = JSON.parse(publicado)
    contrato.components.schemas.AdaptacaoResponse.properties.campo_t6_teste = {
      type: 'string',
    }
    writeFileSync(origem, JSON.stringify(contrato))
    const antes = readFileSync(destino, 'utf8')
    expect(() => verificar(origem, destino)).toThrow(/desatualizados/)
    expect(readFileSync(destino, 'utf8')).toBe(antes)
    execFileSync(process.execPath, [gerador, origem, '-o', destino], {
      stdio: 'pipe',
    })
    expect(readFileSync(destino, 'utf8')).toContain('campo_t6_teste')
    expect(verificar(origem, destino)).toContain('sincronizados')
  })

  it('rejeita tipos editados manualmente e tipos ausentes', () => {
    const { origem, destino } = preparar()
    writeFileSync(
      destino,
      'export interface RespostaManual { titulo: string }\n',
    )
    expect(() => verificar(origem, destino)).toThrow(/desatualizados/)
    rmSync(destino)
    expect(() => verificar(origem, destino)).toThrow(/ausentes/)
  })

  it('falha se o documento OpenAPI não puder ser interpretado', () => {
    const { origem, destino } = preparar()
    writeFileSync(origem, '{ json inválido')
    expect(() => verificar(origem, destino)).toThrow()
  })
})
