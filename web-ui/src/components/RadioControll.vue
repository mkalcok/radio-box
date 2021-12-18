<template>
  <v-container>
    <v-alert
      dense
      outlined
      dismissible
      v-model="alert"
      type="error"
    >
      Je potrebne vybrat radio stanicu.
    </v-alert>
    <v-row
      justify=center
    >
      <v-col
        xl=6
      >
        <v-card
          elevation="2"
        >
          <v-card-title>
            <span class="text-h6 font-weight-light">Radio Player</span>
          </v-card-title>

          <v-card-text class="text-h5 font-weight-bold center-text">
            <v-select
              :items="stations"
              v-model="selected_station"
              item-text="name"
              item-value="id"
              label="Radio Stanice"
            ></v-select>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn icon v-on:click="play">
              <v-icon>mdi-play-circle-outline</v-icon>
            </v-btn>
            <v-btn icon v-on:click="stop">
              <v-icon>mdi-stop-circle-outline</v-icon>
            </v-btn>
          </v-card-actions>

        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
export default {
  name: 'RadioControll',
  data () {
    return {
      stations: [],
      selected_station: "",
      alert: false,
    }
  },
  methods: {
    play: function () {
      if (this.selected_station.id == "") {
        this.alert = true;
        return
      }
      axios
      .post('/play', {"station": this.selected_station})
      .then(response => {
        console.log(response.data)
      })
      .catch(error => {
        console.log(error)
      })
    },
    stop: function () {
      axios
      .get('/stop')
      .then(response => {
        console.log(response.data)
      })
      .catch(error => {
        console.log(error)
      })
    },
  },
  mounted () {
    axios
      .get('/stations')
      .then(response => {
        for (const [station_id, station_name] of Object.entries(response.data.stations)) {
          this.stations.push({"name": station_name, "id": station_id})
        }
      })
      .catch(error => {
        console.log(error)
      })
  }
}
</script>
