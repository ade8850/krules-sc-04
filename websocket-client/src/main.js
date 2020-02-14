import Vue from 'vue'
import App from './App'
import webSocketService from './services/webSocketService'
import store from './store'
import { BootstrapVue } from 'bootstrap-vue'
import LoadScript from 'vue-plugin-load-script'

Vue.config.productionTip = false

Vue.use(BootstrapVue)
Vue.use(LoadScript)

Vue.use(webSocketService, {
  store,
  url: 'ws://127.0.0.1:5678/ws'
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  render: h => h(App),
  store
})
