/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        light:{
          background: "#ffffff",
          text: "#000000",
          border: "#ddd",
          "secondary-bg": "#f3f3f3",
          "hover-bg": "#f1f1f1",
          "table-header-bg": "#9e3203",
          "table-header-text": "#ffffff",
          "button-bg": "linear-gradient(to bottom right, #8B5CF6, #3B82F6)",
          "button-text": "#1F2937",
          "top-bar-bg": "#b85b14",
          "top-bar-text": "#fff",
          "taskbar-bg": "#35495e",
          "taskbar-text": "#fff",
          "active-bg": "#009879",
        },
        dark: {
          background: "#121212",
          text: "#e0e0e0",
          border: "#444",
          "secondary-bg": "#333",
          "hover-bg": "#555",
          "table-header-bg": "#444",
          "table-header-text": "#e0e0e0",
          "button-bg": "#333",
          "button-text": "#e0e0e0",
          "top-bar-bg": "#1e1e1e",
          "top-bar-text": "#e0e0e0",
          "taskbar-bg": "#2d2d2d",
          "taskbar-text": "#cfcfcf",
          "active-bg": "#5a5a5a",
        },
      },
    },
  },
  plugins: [],
}
