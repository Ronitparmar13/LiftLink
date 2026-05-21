/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        liftlink: {
          primary: '#2563eb',
          accent: '#22d3ee',
          dark: '#0f172a',
        },
      },
    },
  },
  plugins: [],
}
