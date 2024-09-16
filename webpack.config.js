const path = require('path');

module.exports = {
  entry: './static/js/main.js', // Your main entry point for the React app
  output: {
    path: path.resolve(__dirname, 'static/dist'), // Output directory
    filename: 'bundle.js' // Output file name
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/, // Matches both .js and .jsx files
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader', // Use Babel loader to transpile React code
          options: {
            presets: ['@babel/preset-react'] // Ensure React preset is included
          }
        }
      },
      {
        test: /\.css$/, // Matches all .css files
        use: ['style-loader', 'css-loader'] // Use style-loader and css-loader
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx'] // Resolve both .js and .jsx extensions
  },
  mode: 'development'
};
