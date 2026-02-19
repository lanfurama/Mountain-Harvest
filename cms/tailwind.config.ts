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
        brand: {
          green: "#2F5233",
          darkGreen: "#1a331d",
          light: "#76885B",
          brown: "#8B5A2B",
          cream: "#F1F0E8",
          orange: "#E85D04",
        },
      },
      fontFamily: {
        sans: ["var(--font-nunito)", "sans-serif"],
        serif: ["var(--font-playfair)", "serif"],
      },
    },
  },
  plugins: [],
};

export default config;
