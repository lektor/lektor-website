const webpack = require("webpack");
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const options = {
  entry: {
    app: "./js/app.js",
    styles: "./scss/main.scss",
  },
  output: {
    path: path.join(__dirname, "..", "assets", "static"),
    filename: "[name].js",
  },
  devtool: "source-map",
  mode: "production",
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: ["@babel/preset-env"],
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
        type: "asset",
      },
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      jQuery: "jquery",
    }),
    new MiniCssExtractPlugin(),
  ],
};

module.exports = options;
