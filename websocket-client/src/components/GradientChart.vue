<template>
  <div class="gradient">
    <!--h1 class="range-label cold">{{ min_label }}</h1>
    <h1 class="range-label mid">{{ mid_label }}</h1>
    <h1 class="range-label hot">{{ max_label }}</h1-->
    <div class="sheet">
      <table>
        <thead>
          <tr>
            <th>Legend</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="cold">{{ min_label }}</td>
          </tr>
          <tr>
            <td class="mid">{{ mid_label }}</td>
          </tr>
          <tr>
            <td class="hot">{{ max_label }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <h2 class="gradient-header">Devices Temperature</h2>
    <ul>
      <li v-for="(device, index) in chartData" :key="index" :class="device.range"  :style="device.position">
        <i class="lnr lnr-pushpin"/>{{ device.id }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'gradient-chart',
  props: ['chartData'],
  watch: {
    chartData () {
      console.log('CHANGE!!!')
    }
  },
  data () {
    return {
      min_label: 'Cold',
      mid_label: 'OK',
      max_label: 'Hot',
      devices: []
    }
  },
  mounted () {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.gradient {
  background: linear-gradient(to right, #00ccff 0%, #ffff66 50%, #cc0000 100%);
}
.gradient-header {
  width: 100%;
  margin-left: 10px;
}
.range-label {
  width: 33%;
  text-align: center;
  display:inline-table;
}
ul {
  padding: 0;
}
li {
  display: table;
  position: relative;
  font-size: x-large
}
.cold {
  color: blue;
}
.mid {
  color: forestgreen;
}
.hot {
  color: yellow;
}
.sheet {
  width: 10%;
  position: relative;
  float: right;
  height: 100%;
}
.sheet table {
  position: absolute;
  bottom: 0;
}
</style>
