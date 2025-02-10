/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        '../templates/**/*.html',     // Theme app templates
        '../../templates/**/*.html',  // Main project templates
        '../../**/templates/**/*.html', // Other Django apps' templates
        '../../static/**/*.css',      // Include Tailwind styles from static files
        '../../static/**/*.js',       // JavaScript files using Tailwind classes
        '../../**/*.py',              // Python files using Tailwind classes (optional)
    ],
    theme: {
        extend: {},
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
