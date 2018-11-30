<template>
  <v-container
    fluid
    fill-height
    grid-list-xl
  >
    <v-toolbar
      app
      class="primary"
    >
      <v-toolbar-items>
        <v-btn
          flat
          dark
          @click='goBack'
        >
          <v-icon left>
            arrow_back
          </v-icon>
          BACK TO DATASET MANAGER
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
  </v-container>

</template>

<script>
  export default {
    props: {
      id: String,
    },
    methods: {
      goBack() {
        this.$router.go(-1);
      }
    }
  }
</script>

<style scoped>
</style>
