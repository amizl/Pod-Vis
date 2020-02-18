<template>
  <v-navigation-drawer :mini-variant="!expand" app permanent fixed class="">
    <v-layout column fill-height align-space-around>
      <v-list three-line class="pt-3">
        <v-list-tile>
          <div v-if="expand">
            <img
              width="100%"
              src="/images/POD-Vis_tag2.jpg"
              alt="POD-Vis: Probing Outcomes Data with Visual analytics"
            />
          </div>
          <div v-else>
            <img
              width="100%"
              src="/images/POD-Vis.jpg"
              alt="POD-Vis: Probing Outcomes Data with Visual analytics"
            />
          </div>
        </v-list-tile>
      </v-list>

      <v-list three-line class="pt-0">
        <v-list-tile
          v-for="item in menuItems"
          :key="item.title"
          :to="item.path"
          active-class="primary text--lighten-5"
        >
          <v-list-tile-action v-if="expand">
            <v-icon color="primary lighten-1">{{ item.icon }}</v-icon>
          </v-list-tile-action>
          <v-tooltip v-else color="primary" right>
            <v-list-tile-action slot="activator">
              <v-icon color="primary lighten-1">{{ item.icon }}</v-icon>
            </v-list-tile-action>
            <span>{{ item.name }}</span>
          </v-tooltip>
          <v-list-tile-content v-if="expand">
            <v-list-tile-title>
              <span> {{ item.name }} </span>
            </v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
      <v-spacer></v-spacer>
      <v-list one-line>
        <v-list-tile @click="expand = !expand">
          <v-tooltip v-if="expand" color="primary" right>
            <v-list-tile-action slot="activator">
              <v-icon color="primary" small>chevron_left</v-icon>
            </v-list-tile-action>
            <span>Collapse menu</span>
          </v-tooltip>
          <v-tooltip v-else color="primary" right>
            <v-list-tile-action slot="activator">
              <v-icon color="primary" small>chevron_right</v-icon>
            </v-list-tile-action>
            <span>Expand menu</span>
          </v-tooltip>
        </v-list-tile>

        <v-list-tile @click="signOutDialog = true">
          <v-list-tile-action v-if="expand">
            <v-icon color="primary">close</v-icon>
          </v-list-tile-action>
          <v-tooltip v-else color="primary" right>
            <v-list-tile-action slot="activator">
              <v-icon color="primary">close</v-icon>
            </v-list-tile-action>
            <span>Sign Out</span>
          </v-tooltip>
          <v-list-tile-content v-if="expand">
            <v-list-tile-title>
              <span class="primary--text"> Sign out </span>
            </v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
      <!-- <v-list class="pb-5">
        <v-list-tile>
          <v-list-tile-action v-if="!expand">
            <img width="20px" src="@/assets/som_icon.svg" alt="IGS Logo" />
          </v-list-tile-action>
          <v-list-tile-content v-if="expand">
            <img src="@/assets/som_logo.svg" alt="IGS Logo" />
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
      expand: false,
      menuItems: [
        {
          name: 'Home Page',
          icon: 'home',
          path: '/homepage',
        },
        {
          name: 'Dataset Manager',
          icon: 'table_chart',
          path: '/datasets',
        },
        // {
        //   name: 'Analysis Summary',
        //   icon: 'bar_chart',
        //   path: '/summary',
        // },
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
      ],
    };
  },
  watch: {
    expand(value) {
      // cache if sidebar is toggled
      if (window.localStorage.expand != value) {
        window.localStorage.expand = value;
      }
    },
  },
  created() {
    // Check if we have cached if the sidebar is toggled
    if ('expand' in window.localStorage) {
      const { expand } = window.localStorage;
      this.expand = eval(expand); // evaluate 'false' or 'true' strings
    } else {
      this.expand = false;
    }
  },
  methods: {
    ...mapActions({
      signUserOut: actions.SIGN_USER_OUT,
    }),
  },
};
</script>
