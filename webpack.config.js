const path = require("path");

module.exports = {
  entry: path.resolve(__dirname, "frontend/src/index.js"),
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "frontend/static/js"),
    publicPath: "/static/js/",                   // Django will serve from /static/js/
  },
  resolve: {
    extensions: [".js", ".jsx"],                 // ← make sure .jsx files are picked up
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        include: path.resolve(__dirname, "frontend/src"),
        loader: "babel-loader",
        options: {
          presets: ["@babel/preset-env", "@babel/preset-react"],
        },
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
      // … any other loaders you need
    ],
  },
  devServer: {
    static: path.resolve(__dirname, "frontend/static"),
    port: 3000,
    hot: true,
  },
};