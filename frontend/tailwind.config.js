/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        agri: {
          green: "#166534",
          lightgreen: "#dcfce7",
          amber: "#92400e",
          lightamber: "#fef3c7",
          red: "#991b1b",
          lightred: "#fee2e2",
        },
      },
    },
  },
  plugins: [],
}
