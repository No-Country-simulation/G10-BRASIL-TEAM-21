import { ThemeToggle } from './ThemeToggle'

export function Header() {
  return (
    <header className="app-header">
      <div>
        <span className="text-secondary">
          Plataforma de aprendizagem
        </span>
      </div>

      <div className="d-flex align-items-center gap-3">
        <ThemeToggle />

        <button className="btn btn-light rounded-circle">
          <i className="bi bi-person" />
        </button>
      </div>
    </header>
  )
}