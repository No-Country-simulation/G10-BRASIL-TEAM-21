import { copyFile, mkdir, readdir } from 'node:fs/promises'

const origem = new URL('../mocks/', import.meta.url)
const destino = new URL('../src/mocks/', import.meta.url)
await mkdir(destino, { recursive: true })
for (const arquivo of await readdir(origem)) {
  if (arquivo.endsWith('.json')) {
    await copyFile(new URL(arquivo, origem), new URL(arquivo, destino))
  }
}
