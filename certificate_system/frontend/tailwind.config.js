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
          dark: "#0b0f19",
          darker: "#060911",
          navy: "#151e36",
          blue: "#3b82f6",
          blueDark: "#1d4ed8",
          gold: "#eab308",
          goldDark: "#a16207"
        }
      }
    },
  },
  plugins: [],
}
