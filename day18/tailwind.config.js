/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            colors: {
                gac: {
                    dark: '#1a1a1a',
                    light: '#f5f5f5',
                    accent: '#4285f4', // Google Blue
                }
            }
        },
    },
    plugins: [],
}
