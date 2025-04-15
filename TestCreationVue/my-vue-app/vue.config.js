module.exports = {
  devServer: {
    port: 8080,
    open: true,
  },
  configureWebpack: {
    // Additional webpack configuration can go here
  },
  // Other Vue CLI configurations can be added as needed
  publicPath: process.env.NODE_ENV === 'production'
  ? '/Senior-Project/'
  : '/'
};