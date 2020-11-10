const webpack = require('webpack');
const fs = require('fs');

const packageJson = fs.readFileSync('./package.json');
const version = JSON.parse(packageJson).version || 0;

module.exports = {
  devServer: {
    proxy: {
      '^/auth': {
        target: 'http://localhost:5000',
      },
      '^/api': {
        target: 'http://localhost:5000',
      },
    },
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        VERSION: '2.0',
        'process.env': {
          PODVIS_VERSION: '"' + version + '"',
        },
      }),
      new webpack.LoaderOptionsPlugin({
        options: {
          rules: [
            {
              test: /\.styl$/,
              loader: ['style-loader', 'css-loader', 'stylus-loader'],
            },
          ],
        },
      }),
    ],
  },
};
