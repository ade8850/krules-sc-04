let webSocketsService = {}

webSocketsService.install = function (Vue, options) {
  let ws = new WebSocket(options.url)
  let reconnectInterval = options.reconnectInterval || 1000

  Vue.prototype.$webSocketsConnect = () => {
    ws = new WebSocket(options.url)
    handleSocketStatusNotification('Connecting...')

    ws.onopen = () => {
      // Restart reconnect intervalg
      console.log('OPEN')
      handleSocketStatusNotification('Connected')
      console.log(ws.readyState)
      reconnectInterval = options.reconnectInterval || 1000
    }

    ws.onmessage = (event) => {
      // New message from the backend - use JSON.parse(event.data)
      console.log('MESSAGE!!!!!')
      console.log(JSON.parse(event.data))
      console.log(event)
      handleNotification(event)
    }

    ws.onclose = (event) => {
      console.log('CLOSE!!!')
      handleSocketStatusNotification('Closed')
      if (event) {
        // Event.code 1000 is our normal close event
        if (event.code !== 1000) {
          let maxReconnectInterval = options.maxReconnectInterval || 3000
          setTimeout(() => {
            if (reconnectInterval < maxReconnectInterval) {
              // Reconnect interval can't be > x seconds
              reconnectInterval += 1000
            }
            Vue.prototype.$webSocketsConnect()
          }, reconnectInterval)
        }
      }
    }

    ws.onerror = (error) => {
      console.log(error)
      handleSocketStatusNotification(error)
      ws.close()
    }
  }

  Vue.prototype.$webSocketsDisconnect = () => {
    // Our custom disconnect event
    ws.close()
  }

  Vue.prototype.$webSocketsSend = (data) => {
    // Send data to the backend - use JSON.stringify(data)
    ws.send(JSON.stringify(data))
  }

  /*
    Here we write our custom functions to not make a mess in one function
  */
  function handleNotification (params) {
    console.log(params)
    let data = JSON.parse(params.data)
    options.store.dispatch('notifications/setNotifications', data)
    options.store.dispatch('notifications/setDevicesMapData', data)
    options.store.dispatch('notifications/setTemperaturesRange', data)
  }

  function handleSocketStatusNotification (params) {
    console.log(params)
    options.store.dispatch('notifications/setSocketStatus', params)
  }
}

export default webSocketsService
