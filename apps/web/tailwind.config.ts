import type { Config } from 'tailwindcss'

const config: Config = {
  content: {
    files: [
      './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
      './src/components/**/*.{js,ts,jsx,tsx,mdx}',
      './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    transform: {
      tsx: (content) => content.replace(/taos:/g, ''),
    },
  },
}

export default config
