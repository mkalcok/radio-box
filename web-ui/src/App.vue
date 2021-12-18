<template>
  <v-app>
    <v-main>
      <RadioControll/>
    </v-main>
  </v-app>
</template>

<script>
import RadioControll from './components/RadioControll';

export default {
  name: 'App',

  components: {
    RadioControll,
  },

  data: () => ({
    //
  }),
};
</script>
