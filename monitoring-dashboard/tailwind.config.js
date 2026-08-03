/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0B0F14",
        panel: "#121821",
        "panel-raised": "#1A222D",
        "panel-line": "#232C38",
        ink: {
          primary: "#E7EDF3",
          muted: "#7C8A9A",
          faint: "#4B5866",
        },
        signal: {
          calm: "#3DDC97",
          watch: "#F2B84B",
          critical: "#F2545B",
        },
        forecast: "#6C8EF5",
      },
      fontFamily: {
        display: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      keyframes: {
        pulseRing: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.55" },
          "50%": { transform: "scale(1.12)", opacity: "0.15" },
        },
        slideIn: {
          from: { transform: "translateX(24px)", opacity: "0" },
          to: { transform: "translateX(0)", opacity: "1" },
        },
        fadeUp: {
          from: { transform: "translateY(6px)", opacity: "0" },
          to: { transform: "translateY(0)", opacity: "1" },
        },
      },
      animation: {
        "pulse-ring": "pulseRing 2.4s cubic-bezier(0.4,0,0.6,1) infinite",
        "slide-in": "slideIn 0.25s ease-out",
        "fade-up": "fadeUp 0.3s ease-out",
      },
    },
  },
  plugins: [],
};
