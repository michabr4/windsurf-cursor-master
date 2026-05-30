/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        cisco: {
          blue:  '#049fd9',
          dark:  '#171f2d',
          navy:  '#1a2332',
          teal:  '#00bceb',
          green: '#6cc04a',
          sky:   '#64bbe3',
        },
      },
    },
  },
  plugins: [],
}
