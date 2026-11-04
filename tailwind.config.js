/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          green: '#9CD296',
          dark: '#263528',
          bg: '#F5F9F4',
          accent: '#7EBF77',
          surface: '#EBF4EA'
        }
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Display"',
          '"SF Pro Text"',
          '"Segoe UI"',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif'
        ]
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(156, 210, 150, 0.15)',
        'glass-hover': '0 16px 40px 0 rgba(156, 210, 150, 0.25)',
        'glass-card': '0 20px 50px rgba(38, 53, 40, 0.05)',
        'inner-glow': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.6)'
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}

