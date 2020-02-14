const namespaced = true

const state = {
  notifications: [],
  devices: [],
  socketStatus: '',
  devicesMapData: {
    positions: [],
    mainPosition: null
  },
  temperatures: []
}

const getters = {
  getNotifications: state => {
    return state.notifications
  },
  getDevices: state => {
    return state.devices
  },
  getNotificationsCount: state => {
    if (!state.notifications) {
      return 0
    }
    return state.notifications.length
  },
  getSocketStatus: state => {
    return state.socketStatus
  },
  getDevicesMapData: state => {
    return state.devicesMapData
  },
  getTemperatureRange: state => {
    return state.temperatures
  }
}

const mutations = {
  changeNotifications: (state, payload) => {
    console.log(payload)
    try {
      let data = JSON.parse(payload)
      if (data.device) {
        if (data.payload.event) {
          state.notifications.push(data.device + ': ' + data.payload.event)
        } else {
          state.notifications.push('New value for ' + data.device + ': ' + data.payload.value)
        }
        for (var d in state.devices) {
          var dev = state.devices[d]
          if (dev) {
            console.log(data.device)
            if (dev.id === data.device) {
              for (var k in data.payload) {
                dev[k] = data.payload[k]
              }
              return
            }
          }
        }
        var newDevice = data.payload
        newDevice['id'] = data.device
        state.devices.push(newDevice)
        console.log(state.devices)
        console.log(state.notifications)
      }
    } catch (err) {
      console.log(err)
      state.notifications.push(payload)
    }
  },
  changeSocketStatus: (state, payload) => {
    console.log('STATUS : ' + payload)
    state.socketStatus = payload
  },
  changeDevicesMapData: (state, payload) => {
    const targetSVG = 'M9,0C4.029,0,0,4.029,0,9s4.029,9,9,9s9-4.029,9-9S13.971,0,9,0z M9,15.93 c-3.83,0-6.93-3.1-6.93-6.93S5.17,2.07,9,2.07s6.93,3.1,6.93,6.93S12.83,15.93,9,15.93 M12.5,9c0,1.933-1.567,3.5-3.5,3.5S5.5,10.933,5.5,9S7.067,5.5,9,5.5 S12.5,7.067,12.5,9z'
    let lastDevice = JSON.parse(payload)
    if (lastDevice.payload.value) {
      var coords = lastDevice.payload.value
      console.log(coords)
      if (coords.length !== 2) {
        console.log(coords.length)
        if (typeof coords === 'string' || coords instanceof String) {
          console.log('IS STRING')
          coords = coords.replace('(', '').replace(')', '').split(',')
        } else {
          return
        }
      }
      if (coords.length === 2) {
        const lastPoisition = {
          id: lastDevice.device,
          color: '#40e583',
          svgPath: targetSVG,
          title: lastDevice.device,
          country: lastDevice.payload.event,
          latitude: parseFloat(coords[0]),
          longitude: parseFloat(coords[1]),
          scale: 1.5,
          zoomLevel: 2.74,
          images: [
            {
              label: 'Devices Map',
              left: 100,
              top: 45,
              color: '#2c82e0',
              labelColor: '#2c82e0',
              labelRollOverColor: '#2c82e0',
              labelFontSize: 20
            }
          ]
        }

        var positions = [
          lastPoisition
        ]

        if (state.devices) {
          console.log('adding devices...')
          for (var d in state.devices) {
            let device = state.devices[d]
            if (device.value && device.id !== lastDevice.device && (typeof device.value === 'string' || device.value instanceof String)) {
              let coords = device.value.replace('(', '').replace(')', '').split(',')
              console.log(coords)
              if (coords.length === 2) {
                var color = '#f0ad4e'
                if (device.status === 'INACTIVE') {
                  color = '#a94442'
                } else if (device.status === 'ACTIVE') {
                  color = '#40e583'
                }
                positions.push(
                  {
                    svgPath: targetSVG,
                    color: color,
                    title: device.id,
                    latitude: parseFloat(coords[0]),
                    longitude: parseFloat(coords[1])
                  }
                )
              }
            }
          }
        }

        state.devicesMapData = {
          positions,
          mainPosition: lastPoisition
        }
      }
    } else {
      if (lastDevice.payload.status) {
        let deviceStatus = lastDevice.payload.status
        let positions = state.devicesMapData.positions
        for (var dx in positions) {
          var device = positions[dx]
          console.log('DEVICE ID')
          console.log(device.id)
          if (device.id === lastDevice.device) {
            var newColor = '#f0ad4e'
            console.log(deviceStatus)
            if (deviceStatus === 'INACTIVE') {
              newColor = '#a94442'
            } else if (deviceStatus === 'ACTIVE') {
              newColor = '#40e583'
            }
            device.color = newColor
            state.devicesMapData = {
              positions,
              mainPosition: device
            }
            return
          }
        }
      }
    }
  },
  changeTemperaturesRange: (state, payload) => {
    const minValue = 20
    const maxValue = 30
    let newDevice = JSON.parse(payload)
    console.log('changeTemperaturesRange')
    console.log(payload)
    console.log(newDevice.payload)
    if (newDevice.payload.value) {
      try {
        var value = parseFloat(newDevice.payload.value)
        if (isNaN(value)) {
          return
        }
        var range = 'mid'
        var position = ((value - minValue) / (maxValue - minValue) * 33) + 33
        if (value < minValue) {
          range = 'cold'
          position = value / minValue * 33
          if (position < 0) {
            position = 0
          }
        } else if (value > maxValue) {
          range = 'hot'
          position = (value / (100 - maxValue) * 33) + 66
          if (position > 90) {
            position = 90
          }
        }
        for (var d in state.temperatures) {
          console.log(newDevice.device)
          let device = state.temperatures[d]
          console.log(device.id)
          if (device.id === newDevice.device) {
            console.log('FOUND!!!')
            device.value = value
            device.range = range
            device.position = {left: position + '%'}
            console.log(state.temperatures)
            return
          }
        }
        state.temperatures.push(
          {
            id: newDevice.device,
            value: value,
            range: range,
            position: {left: position + '%'}
          }
        )
      } catch (err) {
        console.log(err)
      }
    } else {

    }
  }
}

const actions = {
  setNotifications: ({commit}, payload) => {
    commit('changeNotifications', payload)
  },
  setDevicesMapData: ({commit}, payload) => {
    commit('changeDevicesMapData', payload)
  },
  setTemperaturesRange: ({commit}, payload) => {
    commit('changeTemperaturesRange', payload)
  },
  setSocketStatus: ({commit}, payload) => {
    commit('changeSocketStatus', payload)
  }
}

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
