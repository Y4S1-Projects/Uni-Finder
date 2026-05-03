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
				"slide-in-up": "slideInUpToast 0.35s ease-out forwards",
				"modal-enter": "modalEnter 0.2s ease-out forwards",
				"reveal-line": "revealLine 0.8s ease-out forwards",
				blink: "blink 1s step-end infinite",
				pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
			},
			keyframes: {
				slideInUpToast: {
					"0%": { opacity: "0", transform: "translateY(16px)" },
					"100%": { opacity: "1", transform: "translateY(0)" },
				},
				modalEnter: {
					"0%": { opacity: "0", transform: "scale(0.95)" },
					"100%": { opacity: "1", transform: "scale(1)" },
				},
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
				blink: {
					"0%, 49%": { opacity: "1" },
					"50%, 100%": { opacity: "0" },
				},
			},
		},
	},
	corePlugins: {
		preflight: false,
	},
	plugins: [],
};
