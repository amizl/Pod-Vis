module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: ['@vue/airbnb', 'plugin:vue/recommended', '@vue/prettier'],
  plugins: ['vue', 'jsx-a11y', 'import'],
  settings: {
    'import/resolver': 'webpack',
  },
  rules: {
    'import/extensions': 'off',
    'prettier/prettier': [
      'error',
      {
        singleQuote: true,
        trailingComma: 'es5',
      },
    ],
    'func-names': 0,
    'import/no-unresolved': 'off',
    'import/no-extraneous-dependencies': 'off',
    'no-param-reassign': [
      2,
      {
        props: false,
      },
    ],
    'no-underscore-dangle': [0],
  },
  parserOptions: {
    parser: 'babel-eslint',
  },
};
