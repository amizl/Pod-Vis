<template lang='pug'>
  v-toolbar(
    app
    fixed
    dense
  )
    v-toolbar-title(left v-text='title')
    v-spacer
    v-toolbar-items
      v-spacer
      v-btn(
        flat v-for='item in menuItems'
        :key='item.name'
        :to='item.path'
      )
        v-icon(left) {{ item.icon }}
        | {{ item.name }}
    v-spacer
    v-toolbar-items
      v-btn(flat @click='signUserOut') Sign Out

</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import { actions } from '@/store/modules/auth/types';
const { mapActions } = createNamespacedHelpers('auth');

export default {
  data() {
    return {
      title: 'CliO-Vis',
      menuItems: [
        {
          name: 'HOME',
          icon: 'account_circle',
          path: '/',
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

<style scoped>
</style>
