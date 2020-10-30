<template>
  <v-navigation-drawer
    :mini-variant="!showExpanded()"
    mini-variant-width="100"
    app
    permanent
    fixed
  >
    <!-- POD-Vis Logo -->
    <v-list class="pt-3">
      <v-list-item>
        <div v-if="showExpanded()">
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
      </v-list-item>

      <v-list-item class="justify-center">
        <div class="font-weight-medium primary--text">
	  <!--          v{{ VERSION }} -->
	  v1.0.2
	</div>
      </v-list-item>

      <!-- Application links -->
      <v-list-item
        v-for="item in menuItems"
        :key="item.title"
        :to="item.path"
        justify="center"
      >
        <!-- icon without tooltip -->
        <v-list-item-icon v-if="showExpanded()">
          <v-icon color="primary" large>{{ item.icon }}</v-icon>
        </v-list-item-icon>

        <!-- icon with tooltip -->
        <v-tooltip v-else color="primary" right>
          <template v-slot:activator="{ on: tooltip }">
            <v-list-item-action v-on="{ ...tooltip }">
              <v-icon color="primary" large>{{ item.icon }}</v-icon>
            </v-list-item-action>
          </template>
          <span>{{ item.name }}</span>
        </v-tooltip>

        <v-list-item-content class="primary--text">
          <span class="title-1">{{ item.name }}</span>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <!-- SIGN OUT DIALOG -->
    <v-dialog v-model="signOutDialog" width="500" persistent>
      <v-card>
        <v-card-title color="white" primary-title>
          <v-icon color="primary darken-3">warning</v-icon>
          <span class="primary--text text--darken-3 title pl-2">Sign Out</span>
        </v-card-title>
        <v-card-text class="primary primary--text text--lighten-5 pt-4"
          >Are you sure you'd like to sign out?</v-card-text
        >
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="signOutDialog = false"
            ><v-icon left>close</v-icon>Cancel</v-btn
          >
          <v-btn color="primary" @click="signUserOut">Sign Out</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <template v-slot:append>
      <v-list>
        <!-- minimize/expand -->
        <v-list-item
          v-if="$route.name !== 'homepage'"
          @click="expand = !expand"
        >
          <v-list-item-action v-if="showExpanded()">
            <v-icon color="primary" x-large>chevron_left</v-icon>
          </v-list-item-action>

          <v-list-item-action v-else>
            <v-tooltip color="primary" right>
              <template v-slot:activator="{ on: tooltip }">
                <v-icon color="primary" x-large v-on="{ ...tooltip }"
                  >chevron_right</v-icon
                >
              </template>
              <span>Expand menu</span>
            </v-tooltip>
          </v-list-item-action>

          <v-list-item-content class="primary--text">
            <span class="title-1">Minimize menu</span>
          </v-list-item-content>
        </v-list-item>

        <!-- sign out -->
        <v-list-item @click="signOutDialog = true">
          <v-list-item-action v-if="showExpanded()">
            <v-icon color="primary" large>close</v-icon>
          </v-list-item-action>
          <v-tooltip v-else color="primary" right>
            <template v-slot:activator="{ on: tooltip }">
              <v-list-item-action v-on="{ ...tooltip }">
                <v-icon color="primary" large>close</v-icon>
              </v-list-item-action>
            </template>
            <span class="title-1">Sign Out</span>
          </v-tooltip>
          <v-list-item-content class="primary--text">
            <span class="title-1"> Sign out </span>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </template>
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
          name: 'Create Dataset',
          icon: 'library_add',
          path: '/datasets',
        },
        {
          name: 'Saved Datasets',
          icon: 'library_books',
          path: '/study_datasets',
        },
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
    showExpanded() {
      // always expand Sidebar on home page
      if (this.$route.name === 'homepage') {
        return true;
      }
      return this.expand;
    },
  },
};
</script>

<style scoped></style>
