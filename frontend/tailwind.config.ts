import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'brick-red': '#CC5536',
        'light-grey': '#EEEEEE',
        'special-black': '#3C3235',
        'white': '#FFFFFF',
      },
      fontFamily: {
        sans: ['"TWK Lausanne"', '"Helvetica Neue"', 'Arial', 'sans-serif'],
      },
      fontWeight: {
        light: '350',
        normal: '500',
        bold: '700',
      },
      letterSpacing: {
        wide: '0.05em',
      },
      borderRadius: {
        'studio': '2px',
      },
    },
  },
  plugins: [],
};

export default config;

