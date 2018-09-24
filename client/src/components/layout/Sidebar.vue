<template lang='pug'>
  v-navigation-drawer(
    app
    permanent
    fixed
    :mini-variant='!expand'
  )
    v-layout(
      column
      fill-height
    )
      v-toolbar(flat)
        v-list
          v-list-tile
            v-list-tile-title LOGO
      v-list(three-line)
          v-list-tile(
            v-for="item in menuItems"
            :key="item.title"
            :to='item.path'
          )
            v-list-tile-action
              v-icon(x-large) {{ item.icon }}
            v-list-tile-content(v-if='expand')
              v-list-tile-title {{ item.name }}
      v-spacer
      v-list(three-line)
        v-dialog(
          v-model='dialog'
          width='500'
          persistent
        )
          // TODO: fix width for this tile
          v-list-tile(slot='activator' @click='')
            v-list-tile-action
              v-icon(large) power_settings_new
            v-list-tile-content(v-if='expand')
              v-list-tile-title SIGN OUT
          v-card
            v-card-text Are you sure you would like to sign out?
            v-divider
            v-card-actions
              v-spacer
              v-btn(
                @click.native='dialog = false'
              ) CANCEL
              v-btn(
                color='primary'
                @click='signUserOut'
              ) SIGN OUT
        v-list-tile(
          @click='expand = !expand'
        )
          v-list-tile-action
            v-icon(
              v-if='!expand'
            ) keyboard_arrow_right
            v-icon(
              v-else

            ) keyboard_arrow_left
</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import { actions } from '@/store/modules/auth/types';

const { mapActions } = createNamespacedHelpers('auth');

export default {
  data() {
    return {
      dialog: false,
      expand: false,
      menuItems: [
        {
          name: 'DASHBOARD',
          icon: 'dashboard',
          path: '/dashboard',
        },
        {
          name: 'COHORT MANAGER',
          icon: 'group',
          path: '/cohortManager',
        },
        {
          name: 'DATA EXPLORER',
          icon: 'explore',
          path: '/dataExplorer',
        },
        {
          name: 'ANALYSIS TOOL',
          icon: 'bar_chart',
          path: '/analysisTool',
        },
        {
          name: 'DATASET MANAGER',
          icon: 'table_chart',
          path: '/datasetManager',
        },
      ],
    };
  },
  methods: {
    ...mapActions({
      signUserOut: actions.SIGN_USER_OUT,
    }),
  },
};
</script>
