/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts,scss}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: '#3b82f6',
          indigo: '#4f46e5',
          purple: '#8b5cf6',
          dark: '#1e293b',
        }
      },
    },
  },
  plugins: [],
}