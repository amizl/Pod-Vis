<template>
  <v-toolbar app class="white">
    <v-toolbar-title>POD-Vis</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-toolbar-items>
      <v-btn v-for="item in menuItems" :key="item.name" :to="item.path" flat>
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.name }}
      </v-btn>
    </v-toolbar-items>
    <v-spacer></v-spacer>
    <v-toolbar-items>
      <v-btn flat @click="signOutDialog = true">Sign Out</v-btn>
      <v-dialog v-model="signOutDialog" width="500" persistent>
        <v-card>
          <v-card-text class="pa-4"
            >Are you sure you'd like to sign out?</v-card-text
          >
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="signOutDialog = false">Cancel</v-btn>
            <v-btn color="primary darken-4" @click="signUserOut"
              >Sign out</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-toolbar-items>
  </v-toolbar>
</template>

<script>
import { actions } from '@/store/modules/auth/types';
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      signOutDialog: false,
      menuItems: [
        {
          name: 'Dashboard',
          icon: 'dashboard',
          path: '/dashboard',
        },
        {
          name: 'Dataset Manager',
          icon: 'table_chart',
          path: '/datasets',
        },
        {
          name: 'Cohort Manager',
          icon: 'group',
          path: '/cohorts',
        },
        // {
        //   name: 'Data Explorer',
        //   icon: 'explore',
        //   path: '/explore',
        // },
        {
          name: 'Analysis',
          icon: 'bar_chart',
          path: '/analysis',
        },
      ],
    };
  },
  methods: {
    ...mapActions('auth', {
      signUserOut: actions.SIGN_USER_OUT,
    }),
  },
};
</script>

<style scoped></style>
