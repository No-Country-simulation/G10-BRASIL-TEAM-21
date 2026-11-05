import { useEffect, useState } from 'react'

export type Theme = 'light' | 'dark'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem('adaptai-theme')

    return savedTheme === 'dark' ? 'dark' : 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute(
      'data-bs-theme',
      theme
    )

    localStorage.setItem('adaptai-theme', theme)
  }, [theme])

  function toggleTheme() {
    setTheme((current) =>
      current === 'light' ? 'dark' : 'light'
    )
  }

  return {
    theme,
    toggleTheme,
  }
}