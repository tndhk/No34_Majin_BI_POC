import js from '@eslint/js';
import globals from 'globals';
import prettierConfig from 'eslint-config-prettier';

export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/.venv/**',
      '**/__pycache__/**',
      '**/.claude/**',
      '**/.agent/**',
      '**/.github/**',
      '**/.pytest_cache/**',
      '**/.ruff_cache/**',
      '**/.wrangler/**',
      '**/*.html',
      '**/*.csv',
      '**/memories/**',
      '**/package-lock.json',
    ],
  },
  js.configs.recommended,
  prettierConfig,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021,
      },
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': 'warn',
    },
  },
];
