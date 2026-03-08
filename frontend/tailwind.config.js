/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./src/**/*.{js,jsx}"],
	theme: {
		extend: {
			animation: {
				blob: "blob 7s infinite",
				shimmer: "shimmer 2s linear infinite",
				float: "float 6s ease-in-out infinite",
				fadeIn: "fadeIn 0.6s ease-in",
				slideUp: "slideUp 0.8s ease-out",
				pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
			},
			keyframes: {
				blob: {
					"0%, 100%": { transform: "translate(0, 0) scale(1)" },
					"33%": { transform: "translate(30px, -50px) scale(1.1)" },
					"66%": { transform: "translate(-20px, 20px) scale(0.9)" },
				},
				shimmer: {
					"0%": { backgroundPosition: "-200% 0" },
					"100%": { backgroundPosition: "200% 0" },
				},
				float: {
					"0%, 100%": { transform: "translateY(0px)" },
					"50%": { transform: "translateY(-20px)" },
				},
				fadeIn: {
					"0%": { opacity: "0" },
					"100%": { opacity: "1" },
				},
				slideUp: {
					"0%": { transform: "translateY(30px)", opacity: "0" },
					"100%": { transform: "translateY(0)", opacity: "1" },
				},
			},
		},
	},
	corePlugins: {
		preflight: false,
	},
	plugins: [],
};
