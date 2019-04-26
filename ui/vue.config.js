const webpack = require('webpack');

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
