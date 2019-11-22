<template>
  <v-container fluid>
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Home Page</v-toolbar-title>
    </v-toolbar>
    <v-layout fill-height>
      <!-- <v-layout align-center justify-center> -->
      <v-flex xs12>
         <v-tabs slider-color="primary" grow>
           <v-tab>
             <span class="">My Clinical Data Collections</span>
           </v-tab>
           <v-tab-item>
             <collection-table class="pb-1" :show_public_collections="false"></collection-table>
           </v-tab-item>

           <v-tab>
             <span class="">Public Clinical Data Collections</span>
           </v-tab>
           <v-tab-item>
             <collection-table class="pb-1" :show_public_collections="true"></collection-table>
           </v-tab-item>

	 </v-tabs>
	
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dashboard/types';

import CollectionTable from '@/components/dashboard/CollectionTable.vue';

export default {
  components: {
    CollectionTable,
  },
  computed: {
  },
  created() {
  },
  methods: {
  },
};
</script>

<style scoped></style>
