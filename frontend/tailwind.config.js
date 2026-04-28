/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./src/**/*.{js,jsx}"],
	theme: {
		extend: {
			fontFamily: {
				sans: ['"Inter"', "system-ui", "-apple-system", "sans-serif"],
			},
			animation: {
				shimmer: "shimmer 2s linear infinite",
				fadeIn: "fadeIn 0.6s ease-out forwards",
				slideUp: "slideUp 0.7s ease-out forwards",
				"fade-in-up": "fadeInUp 0.6s ease-out forwards",
				"reveal-line": "revealLine 0.8s ease-out forwards",
				pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
			},
			keyframes: {
				shimmer: {
					"0%": { backgroundPosition: "-200% 0" },
					"100%": { backgroundPosition: "200% 0" },
				},
				fadeIn: {
					"0%": { opacity: "0" },
					"100%": { opacity: "1" },
				},
				slideUp: {
					"0%": { transform: "translateY(30px)", opacity: "0" },
					"100%": { transform: "translateY(0)", opacity: "1" },
				},
				fadeInUp: {
					"0%": { transform: "translateY(24px)", opacity: "0" },
					"100%": { transform: "translateY(0)", opacity: "1" },
				},
				revealLine: {
					"0%": { width: "0%" },
					"100%": { width: "100%" },
				},
			},
		},
	},
	corePlugins: {
		preflight: false,
	},
	plugins: [],
};
