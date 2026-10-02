import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: { 
          50:'#f0f4ff', 
          100:'#e0e9ff', 
          500:'#3b5bdb', 
          600:'#364fc7', 
          700:'#2f4ac7', 
          800:'#1e3a8a', 
          900:'#1e3070' 
        },
        campus: { 
          primary:'#3b5bdb', 
          secondary:'#7c3aed', 
          accent:'#0ea5e9' 
        }
      }
    },
  },
  plugins: [],
}
export default config
