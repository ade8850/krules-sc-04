<template>
  <div>
    <!--p>
      <a href="">Github front-end</a> |
      <a href="https://github.com/latovicalmin/nodejs-websockets" target="_blank">Github back-end</a>
    </p-->
    <h1>{{ msg }}</h1>
    <span>Socket Status : {{ socketStatus }}</span> |
    <span @click="connect" style="color: green; cursor: pointer">Connect websockets</span> |
    <span @click="disconnect" style="color: red; cursor: pointer">Disconnect websockets</span>
    <div class="panel">
      <div class="panel-heading">
        <h3 class="panel-title">Devices</h3>
        <b-dropdown id="dropdown-1" class="m-md-2" no-caret>
          <template v-slot:button-content>
            <div>
              <a href="#" class="dropdown-toggle icon-menu" data-toggle="dropdown">
                <i class="lnr lnr-alarm"></i>
                <span class="badge bg-danger">{{ notificationsCount }}</span>
              </a>
            </div>
          </template>
          <b-dropdown-item v-for="(notification, index) in notifications" :key="index">{{ notification }}</b-dropdown-item>
        </b-dropdown>
        <div class="right">
          <button type="button" class="btn-toggle-collapse" @click="togglePanel"><i class="lnr lnr-chevron-up"></i></button>
        </div>
      </div>
      <div class="panel-body no-padding">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Device id</th>
              <th>Class</th>
              <th>Value</th>
              <th>Event</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(device, index) in devices" :key="index">
              <td><a href="#">{{ device.id }}</a></td>
              <td>{{ device.device_class }}</td>
              <td>
                <span v-if="device.device_class == 'class-b'" class="fa fa-map-marker"></span>
                {{ device.value }}
                <span v-if="device.device_class == 'class-a'">°C</span>
              </td>
              <td v-if="device.event_class == 'cheering'" class="alert alert-info"><i class="fa fa-info-circle"></i>{{ device.event }}</td>
              <td v-else-if="device.event_class == 'warning'" class="alert-warning"><i class="fa fa-warning"></i>{{ device.event }}</td>
              <td v-else-if="device.event_class == 'critical'" class="alert-danger"><i class="fa fa-times-circle"></i>{{ device.event }}</td>
              <td v-else>{{ device.event }}</td>
              <td>
                <span v-if="device.status == 'ACTIVE'" class="label label-success">{{ device.status }}</span>
                <span v-else-if="device.status == 'READY'" class="label label-warning">{{ device.status }}</span>
                <span v-else class="label label-danger">{{ device.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="graph-content">
          <line-map
              :map-data="lineMapData"
              style="width: 50%;"
            />
          <gradient-chart
              :chartData="temperatureChartData"
              style="width: 50%;"
            />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LineMap from './LineMap'
import GradientChart from './GradientChart'

import JQuery from 'jquery'
let $ = JQuery

export default {
  name: 'Dashboard',
  components: {
    LineMap,
    GradientChart
  },
  data () {
    return {
      msg: 'KRules Dashboard',
      collapsed: false
    }
  },
  computed: {
    notifications () {
      return this.$store.getters['notifications/getNotifications']
    },
    devices () {
      return this.$store.getters['notifications/getDevices']
    },
    notificationsCount () {
      return '' + this.$store.getters['notifications/getNotificationsCount']
    },
    socketStatus () {
      return this.$store.getters['notifications/getSocketStatus']
    },
    lineMapData () {
      return this.$store.getters['notifications/getDevicesMapData']
    },
    temperatureChartData () {
      return this.$store.getters['notifications/getTemperatureRange']
    }
  },
  methods: {
    connect () {
      console.log('connecting...')
      this.$webSocketsConnect()
    },
    disconnect () {
      this.$webSocketsDisconnect()
    },
    togglePanel () {
      this.collapsed = !this.collapsed
      $('table')[0].hidden = this.collapsed
      var btn = $('.panel .btn-toggle-collapse')[0]
      var i = btn.children[0]
      if (this.collapsed) {
        i.className = 'lnr lnr-chevron-down'
      } else {
        i.className = 'lnr lnr-chevron-up'
      }
    }
  },
  beforeMount () {
    this.connect()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.row-equal .flex {
    .va-card {
      height: 100%;
    }
  }

  .dashboard {
    .va-card {
      margin-bottom: 0 !important;
    }
  }

  table {
    text-align: center;
  }

  th {
    text-align: center;
  }

  .panel-title {
    text-align: center;
  }

  .dropdown-menu {
    min-width: 50px!important;
  }

  .graph-content {
    margin-top: 5vh;
    display: flex;
    height: 65vh;
  }
</style>
