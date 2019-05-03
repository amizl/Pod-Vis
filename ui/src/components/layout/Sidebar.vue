<template>
  <v-navigation-drawer :mini-variant="!expand" app permanent fixed flat>
    <v-layout column fill-height align-space-around>
      <v-toolbar flat class="white">
        <v-list>
          <v-list-tile> <v-list-tile-title></v-list-tile-title> </v-list-tile>
        </v-list>
      </v-toolbar>
      <v-list two-line>
        <v-list-tile
          v-for="item in menuItems"
          :key="item.title"
          :to="item.path"
          active-class="primary--text-darken-4"
        >
          <v-list-tile-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-tile-action>
          <v-list-tile-content v-if="expand">
            <v-list-tile-title>{{ item.name }}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
      <v-spacer></v-spacer>
      <v-list two-line>
        <v-list-tile @click="signOutDialog = true">
          <v-list-tile-action>
            <v-icon>exit_to_app</v-icon>
          </v-list-tile-action>
          <v-list-tile-content v-if="expand">
            <v-list-tile-title>Sign out</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-tooltip right>
          <v-list-tile slot="activator" @click="expand = !expand">
            <v-list-tile-action>
              <v-icon v-if="!expand" small>keyboard_arrow_right</v-icon>
              <v-icon v-else small>keyboard_arrow_left</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          <span v-if="!expand">Expand</span> <span v-else>Collapse</span>
        </v-tooltip>
      </v-list>
      <v-list class="pb-5">
        <v-list-tile>
          <v-list-tile-action v-if="!expand">
            <img width="20px" src="@/assets/som_igs_icon.svg" alt="IGS Logo" />
          </v-list-tile-action>
          <v-list-tile-content v-if="expand">
            <img src="@/assets/som_igs_logo.svg" alt="IGS Logo" />
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-layout>

    <!-- SIGN OUT DIALOG -->
    <v-dialog v-model="signOutDialog" width="500" persistent>
      <v-card>
        <v-card-title primary-title>
          <v-icon>warning</v-icon>
          <span class="title pl-2">Sign Out</span>
        </v-card-title>
        <v-card-text>Are you sure you'd like to sign out?</v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="signOutDialog = false">Cancel</v-btn>
          <v-btn color="primary darken-4" @click="signUserOut">Sign out</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-navigation-drawer>
</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import { actions } from '@/store/modules/auth/types';

const { mapActions } = createNamespacedHelpers('auth');

export default {
  data() {
    return {
      signOutDialog: false,
      expand: true,
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
        {
          name: 'Data Explorer',
          icon: 'explore',
          path: '/explore',
        },
        {
          name: 'Analysis Tool',
          icon: 'bar_chart',
          path: '/analysis',
        },
      ],
    };
  },
  watch: {
    expand(value) {
      // cache if sidebar is toggled
      window.localStorage['expand'] = value;
    },
  },
  created() {
    // Check if we have cached if the sidebar is toggled
    if ('expand' in window.localStorage) {
      const expand = window.localStorage['expand'];
      this.expand = eval(expand); // evaluate 'false' or 'true' strings
    } else {
      this.expand = true;
    }
  },
  methods: {
    ...mapActions({
      signUserOut: actions.SIGN_USER_OUT,
    }),
  },
};
</script>

<style scoped>
/* Need to modify vuetify's stylus variables */
</style>
