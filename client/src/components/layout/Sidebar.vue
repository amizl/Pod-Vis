<template lang="pug">
  v-navigation-drawer(
    app
    permanent
    fixed
    :mini-variant='!expand'
    flat
    floating
  )
    v-layout(
      column
      fill-height
      align-space-around
    )
      v-toolbar(flat).white
        v-list
          v-list-tile
            v-list-tile-title
      v-list(two-line )
          v-list-tile(
            v-for="item in menuItems"
            :key="item.title"
            :to='item.path'
            active-class='secondary--text'
          )
            v-list-tile-action
              v-icon {{ item.icon }}
            v-list-tile-content(v-if='expand')
              v-list-tile-title {{ item.name }}
      v-spacer
      v-list(two-line)
        v-dialog(
          v-model='dialog'
          width='500'
          persistent
        )
          // TODO: fix width for this tile
          v-list-tile(slot='activator' @click='')
            v-list-tile-action
              v-icon exit_to_app
            v-list-tile-content(v-if='expand')
              v-list-tile-title Sign Out
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
              small
              v-if='!expand'
            ) keyboard_arrow_right
            v-icon(
              small
              v-else
            ) keyboard_arrow_left
      v-list.pb-5
        v-list-tile
          v-list-tile-action
            img(
              v-if='expand'
              src='@/assets/som_igs_logo.svg'
            )
            img(
              v-else
              src='@/assets/som_igs_icon.svg'
              width='20px'
            )
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
          name: 'Analysis Tool',
          icon: 'bar_chart',
          path: '/analysis',
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

<style scoped>
/* Need to modify vuetify's stylus variables */
</style>
