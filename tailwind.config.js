/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#F7F7FB",
          card: "#FFFFFF",
          elevated: "#FAFBFD",
          secondary: "#F0F2F7",
        },
        primary: "#A8C5DA",
        secondary: "#DCEAF4",
        accent: "#6BA3D4",
        text: {
          primary: "#1F2933",
          secondary: "#6B7280",
          tertiary: "#9CA3AF",
        },
        border: "#E5E7EB",
        "border-light": "#F0F0F4",
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        info: "#3B82F6",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      fontSize: {
        xs: ["12px", { lineHeight: "16px", letterSpacing: "0.3px" }],
        sm: ["13px", { lineHeight: "18px", letterSpacing: "0.2px" }],
        base: ["14px", { lineHeight: "20px", letterSpacing: "0.2px" }],
        lg: ["15px", { lineHeight: "22px", letterSpacing: "0.1px" }],
        xl: ["16px", { lineHeight: "24px" }],
        "2xl": ["18px", { lineHeight: "28px" }],
        "3xl": ["20px", { lineHeight: "32px" }],
      },
      spacing: {
        1: "8px",
        2: "16px",
        3: "24px",
        4: "32px",
        5: "40px",
        6: "48px",
        7: "56px",
        8: "64px",
      },
      borderRadius: {
        DEFAULT: "12px",
        xs: "6px",
        sm: "8px",
        md: "12px",
        lg: "16px",
        xl: "20px",
      },
      boxShadow: {
        xs: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        sm: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        base: "0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        md: "0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        lg: "0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        xl: "0 25px 50px -12px rgba(0, 0, 0, 0.12)",
        inner: "inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)",
        none: "none",
      },
      transitionDuration: {
        100: "100ms",
        200: "200ms",
        300: "300ms",
        400: "400ms",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { transform: "translateY(8px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "slide-down": {
          "0%": { transform: "translateY(-8px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.8" },
        },
        "scale-up": {
          "0%": { transform: "scale(0.95)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fade-in 200ms ease-in-out",
        "slide-up": "slide-up 300ms ease-out",
        "slide-down": "slide-down 300ms ease-out",
        "pulse-soft": "pulse-soft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "scale-up": "scale-up 200ms ease-out",
      },
    },
  },
  plugins: [],
};
