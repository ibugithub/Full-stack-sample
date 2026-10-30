import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

export default {
    darkMode: ["class"],
    content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
  	extend: {
  		colors: {
                // Shared template palette. Blue and yellow are accent colors;
                // red and green remain available for error/success messages.
                blue: {
                    50: '#eff6ff', 100: '#dbeafe', 200: '#bfd8ff',
                    300: '#8cbcff', 400: '#4388f5', 500: '#0066eb',
                    600: '#0056cc', 700: '#004bb5', 800: '#003b8f',
                    900: '#123362', 950: '#142033',
                },
                yellow: {
                    50: '#fffbea', 100: '#fff4c2', 200: '#ffe680',
                    300: '#ffd21a', 400: '#ffd21a', 500: '#efbd00',
                    600: '#996b00', 700: '#795200', 800: '#634400',
                    900: '#503900', 950: '#302100',
                },
                gray: {
                    50: '#f7f8fa', 100: '#f1f3f6', 200: '#e2e6ec',
                    300: '#cbd2dc', 400: '#8c97a7', 500: '#657184',
                    600: '#4d596b', 700: '#354154', 800: '#253043',
                    900: '#182230', 950: '#101820',
                },
                slate: {
                    50: '#f7f8fa', 100: '#f1f3f6', 200: '#e2e6ec',
                    300: '#cbd2dc', 400: '#8c97a7', 500: '#657184',
                    600: '#4d596b', 700: '#354154', 800: '#253043',
                    900: '#182230', 950: '#101820',
                },
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		}
  	}
  },
  plugins: [animate],
} satisfies Config;
