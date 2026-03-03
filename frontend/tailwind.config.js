/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ["'JetBrains Mono'", "Consolas", "monospace"],
      },
      colors: {
        surface: {
          0: "#0d1117",
          1: "#161b22",
          2: "#21262d",
          3: "#30363d",
        },
        brand: {
          blue: "#58a6ff",
          green: "#3fb950",
          yellow: "#d29922",
          red: "#f85149",
          purple: "#bc8cff",
          orange: "#f0883e",
        },
      },
      animation: {
        blink: "blink 1s step-end infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-in": "slideIn 0.25s ease-out",
      },
      keyframes: {
        blink: { "0%,100%": { opacity: 1 }, "50%": { opacity: 0 } },
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideIn: { from: { opacity: 0, transform: "translateY(8px)" }, to: { opacity: 1, transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
};
