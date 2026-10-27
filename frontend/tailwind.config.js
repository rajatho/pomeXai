/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Fraunces', 'Georgia', 'serif'],
      },
      colors: {
        pomegranate: {
          50: '#fdf2f4',
          100: '#fce7eb',
          200: '#f9d0d9',
          300: '#f4a9ba',
          400: '#ec7593',
          500: '#df4770',
          600: '#c92857',
          700: '#a91d47',
          800: '#8d1b3f',
          900: '#781a39',
        },
        leaf: {
          50: '#f3faf4',
          100: '#e3f5e7',
          200: '#c8ead0',
          300: '#9dd8ac',
          400: '#6bbd80',
          500: '#46a261',
          600: '#34824c',
          700: '#2b683f',
          800: '#255334',
          900: '#1f452c',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
