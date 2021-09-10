<template>
  <div class="container">
      <div id="app">


        <img alt="Vue logo" src="./assets/logo.png" width="128">

        <h1>Cookies</h1>
        <p>
          It's like <a href="https://create-react-app.dev/" >create-react-app</a> but for your terraform. Fill the form to get your terraform ;)
        </p>

<br>
<!-- Place this tag where you want the button to render. -->
<a class="github-button" href="https://github.com/diggerhq/cookies" data-color-scheme="no-preference: dark; light: dark; dark: dark_high_contrast;" data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star diggerhq/cookies on GitHub">Star</a>
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
  },
  mounted() {
    let url = new URL(window.location.href);
    const token = url.searchParams.get("token");
    // const cliCallback = url.searchParams.get("cli_callback");
    if (token) {
      localStorage.setItem("authToken", token);
      url.searchParams.delete("token");
      window.location.replace(url.href);
    }    
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
