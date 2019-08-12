<template>
  <v-navigation-drawer :mini-variant="!expand" app permanent fixed class="">
    <v-layout column fill-height align-space-around>
      <v-toolbar extended flat color="white">
        <v-list>
          <v-list-tile>
            <v-list-tile-action v-if="!expand">
              <!-- <img
                width="55px"
                src="@/assets/C-2.png"
                alt="IGS Logo"
                class="rounded-lg mt-3"
              /> -->
              <img width="100px" src="@/assets/Clio-Vis-1.png" alt="IGS Logo" />
            </v-list-tile-action>
            <v-list-tile-content>
              <img width="100%" src="@/assets/Clio-Vis-1.png" alt="IGS Logo" />
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
      </v-toolbar>
      <v-list three-line class="pt-0">
        <v-list-tile
          v-for="item in menuItems"
          :key="item.title"
          :to="item.path"
          active-class="primary text--lighten-4"
        >
          <v-list-tile-action>
            <v-icon color="primary lighten-4">{{ item.icon }}</v-icon>
          </v-list-tile-action>
          <v-list-tile-content v-if="expand">
            <v-list-tile-title>
              <span class="primary--text text--lighten-3">
                {{ item.name }}
              </span>
            </v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
      <v-spacer></v-spacer>
      <v-list one-line>
        <v-list-tile @click="signOutDialog = true">
          <v-list-tile-action>
            <v-icon color="primary">exit_to_app</v-icon>
          </v-list-tile-action>
          <v-list-tile-content v-if="expand">
            <v-list-tile-title>
              <span class="primary--text"> Sign out </span>
            </v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-tooltip color="primary" right>
          <v-list-tile slot="activator" @click="expand = !expand">
            <v-list-tile-action>
              <v-icon v-if="!expand" color="primary" small
                >keyboard_arrow_right</v-icon
              >
              <v-icon v-else color="primary" small>keyboard_arrow_left</v-icon>
            </v-list-tile-action>
          </v-list-tile>
          <span v-if="!expand">Expand</span> <span v-else>Collapse</span>
        </v-tooltip>
      </v-list>
      <!-- <v-list class="pb-5">
        <v-list-tile>
          <v-list-tile-action v-if="!expand">
            <img width="20px" src="@/assets/som_igs_icon.svg" alt="IGS Logo" />
          </v-list-tile-action>
          <v-list-tile-content v-if="expand">
            <img src="@/assets/som_igs_logo.svg" alt="IGS Logo" />
          </v-list-tile-content>
        </v-list-tile>
      </v-list> -->
    </v-layout>

    <!-- SIGN OUT DIALOG -->
    <v-dialog v-model="signOutDialog" width="500" persistent>
      <v-card>
        <v-card-title color="white" primary-title>
          <v-icon color="primary darken-3">warning</v-icon>
          <span class="primary--text text--darken-3 title pl-2">Sign Out</span>
        </v-card-title>
        <v-card-text class="primary primary--text text--lighten-4"
          >Are you sure you'd like to sign out?</v-card-text
        >
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="primary lighten-3" @click="signOutDialog = false"
            >Cancel</v-btn
          >
          <v-btn color="primary" @click="signUserOut">Sign Out</v-btn>
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
        // {
        //   name: 'Cohort Manager',
        //   icon: 'group',
        //   path: '/cohorts',
        // },
        // {
        //   name: 'Data Explorer',
        //   icon: 'explore',
        //   path: '/explore',
        // },
        // {
        //   name: 'Analysis Tool',
        //   icon: 'bar_chart',
        //   path: '/analysis',
        // },
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
.foo {
  background-color: #54d1db;
}

/* Need to modify vuetify's stylus variables */
</style>
