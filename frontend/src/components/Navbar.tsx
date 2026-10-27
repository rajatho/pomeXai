import { NavLink } from 'react-router-dom'
import { Moon, Sun, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'

const links = [
  { to: '/', label: 'Home' },
  { to: '/upload', label: 'Predict' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/prediction', label: 'Result' },
  { to: '/history', label: 'History' },
  { to: '/about', label: 'About' },
]

export default function Navbar() {
  const { dark, toggle } = useTheme()
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-leaf-200/60 bg-white/85 backdrop-blur dark:border-leaf-800 dark:bg-gray-950/90">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <NavLink to="/" className="font-display text-2xl tracking-tight text-pomegranate-700 dark:text-pomegranate-400">
          PomeXAI
        </NavLink>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-leaf-100 text-leaf-800 dark:bg-leaf-900 dark:text-leaf-200'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
          <button
            onClick={toggle}
            className="ml-2 rounded-lg p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
            aria-label="Toggle dark mode"
          >
            {dark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
        </nav>

        <div className="flex items-center gap-2 md:hidden">
          <button onClick={toggle} className="rounded-lg p-2" aria-label="Toggle dark mode">
            {dark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
          <button onClick={() => setOpen(!open)} className="rounded-lg p-2" aria-label="Menu">
            {open ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-gray-200 px-4 py-2 md:hidden dark:border-gray-800">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              onClick={() => setOpen(false)}
              className="block rounded-lg px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200"
            >
              {l.label}
            </NavLink>
          ))}
        </div>
      )}
    </header>
  )
}
