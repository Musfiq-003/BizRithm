/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        foreground: '#ededed',
        primary: {
          DEFAULT: '#6366f1', // Indigo
          hover: '#4f46e5',
        },
        card: {
          DEFAULT: '#121212',
          border: '#262626',
        },
        accent: {
          DEFAULT: '#06b6d4', // Cyan
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass': 'linear-gradient(to bottom right, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01))',
      }
    },
  },
  plugins: [],
}
