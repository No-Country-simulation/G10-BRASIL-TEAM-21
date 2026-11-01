import { execFile } from 'node:child_process'
import { mkdtemp, readFile, rm, rmdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parseArgs, promisify } from 'node:util'

const executar = promisify(execFile)
const { values } = parseArgs({
  options: { source: { type: 'string' }, output: { type: 'string' } },
})
const origem = resolve(
  values.source ??
    fileURLToPath(new URL('../../backend/docs/openapi.json', import.meta.url)),
)
const destino = resolve(
  values.output ??
    fileURLToPath(new URL('../src/api/schema.d.ts', import.meta.url)),
)
const gerador = fileURLToPath(
  new URL('../node_modules/openapi-typescript/bin/cli.js', import.meta.url),
)

async function verificar() {
  let atual
  try {
    atual = await readFile(destino, 'utf8')
  } catch (erro) {
    if (erro.code !== 'ENOENT') throw erro
    throw new Error(
      'Tipos da API ausentes. Execute npm run gen:api e inclua src/api/schema.d.ts no PR.',
    )
  }

  const pasta = await mkdtemp(join(tmpdir(), 'adaptai-openapi-'))
  const temporario = join(pasta, 'schema.d.ts')
  try {
    await executar(process.execPath, [gerador, origem, '-o', temporario])
    const esperado = await readFile(temporario, 'utf8')
    if (atual !== esperado) {
      throw new Error(
        'Tipos da API desatualizados. Execute npm run gen:api e inclua o contrato e src/api/schema.d.ts no mesmo PR.',
      )
    }
    console.log('Tipos da API sincronizados com o OpenAPI.')
  } finally {
    await rm(temporario, { force: true })
    await rmdir(pasta)
  }
}

try {
  await verificar()
} catch (erro) {
  console.error(erro.message)
  process.exitCode = 1
}
