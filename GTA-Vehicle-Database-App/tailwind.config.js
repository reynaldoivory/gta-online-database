/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gta: {
          dark: '#0a0a0f',
          darker: '#05050a',
          purple: '#9b4dca',
          blue: '#3b82f6',
          orange: '#f97316',
          green: '#22c55e',
          red: '#ef4444',
          gold: '#eab308'
        }
      }
    },
  },
  plugins: [],
}
