<template>
  <div class="container">
      <div id="app">
        <img alt="Vue logo" src="./assets/logo.png" width="128">
        <h1>Cookies</h1>
        <p>
          It's like <a href="https://create-react-app.dev/" >create-react-app</a> but for your terraform
        </p>

      </div>
        <Main/>
        <hr>
        <Footer/>
  </div>
</template>

<script>
import Main from './components/Main.vue'
import Footer from './components/Footer.vue'

export default {
  name: 'App',
  components: {
    Main,
    Footer
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
