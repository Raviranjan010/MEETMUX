/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#07100E',
        surface: '#0E1916',
        'surface-elevated': '#152420',
        amber: '#F5A623',
        green: '#39C878',
        red: '#EF5350',
        white: '#F4F1E8',
        muted: '#87938D',
        'muted-dark': '#2B3B35',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '3px',
        sm: '2px',
        md: '4px',
        lg: '6px',
      },
    },
  },
  plugins: [],
}
