var webpack = require("webpack");
var path = require("path");
var MiniCssExtractPlugin = require("mini-css-extract-plugin");

var options = {
  entry: {
    app: "./js/app.js",
    styles: "./scss/main.scss",
  },
  output: {
    path: path.dirname(__dirname) + "/assets/static",
    filename: "[name].js",
  },
  devtool: "cheap-module-source-map",
  mode: "production",
  resolve: {
    modules: ["node_modules"],
    extensions: ["", ".js"],
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ["es2015"],
            },
          },
        ],
      },
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.(woff2?|ttf|eot|svg|png)(\?.*?)?$/,
        use: ["file"],
      },
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
    new MiniCssExtractPlugin(),
  ],
};

module.exports = options;
