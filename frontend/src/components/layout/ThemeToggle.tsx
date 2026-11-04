import { useTheme } from '../../hooks/useTheme'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      type="button"
      className="btn btn-outline-secondary rounded-circle"
      onClick={toggleTheme}
      aria-label={
        theme === 'light'
          ? 'Ativar modo escuro'
          : 'Ativar modo claro'
      }
      title={
        theme === 'light'
          ? 'Ativar modo escuro'
          : 'Ativar modo claro'
      }
    >
      <i
        className={
          theme === 'light'
            ? 'bi bi-moon-stars'
            : 'bi bi-sun'
        }
      />
    </button>
  )
}