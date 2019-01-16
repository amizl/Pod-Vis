const webpack = require('webpack');

module.exports = {
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
