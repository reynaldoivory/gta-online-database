// ESLint 9 flat config for the GTA Vehicle Database Vite app.
// Closes the monorepo CLAUDE.md-named lint gap (this app had no ESLint).
// Plain React 18 JSX (no TypeScript) on Vite, so this mirrors the standard
// Vite React template + the sibling apps' conventions: react-hooks +
// react-refresh, with js.recommended rules merged explicitly (not via a
// spread that a later `rules` key would silently override).
import js from '@eslint/js';
import globals from 'globals';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default [
  // Build output + deps
  { ignores: ['dist/**', 'node_modules/**'] },

  // Vite / PostCSS / Tailwind config files — Node context
  {
    files: ['*.config.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: { ...globals.node },
    },
    rules: { ...js.configs.recommended.rules },
  },

  // React application source — browser context
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: { ...globals.browser },
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // Mark JSX-referenced identifiers as used so no-unused-vars doesn't
      // false-positive on components/icons used only inside JSX.
      'react/jsx-uses-react': 'error',
      'react/jsx-uses-vars': 'error',
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      'no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      // Quality gates (match the apps)
      'max-lines': ['warn', { max: 300, skipBlankLines: true, skipComments: true }],
      complexity: ['warn', 10],
    },
  },
];
