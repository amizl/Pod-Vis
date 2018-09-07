<template lang='pug'>
  v-toolbar(app dense color='white')
    v-toolbar-title(left v-text='title')
    v-spacer
    v-toolbar-items
      v-btn(
        flat v-for='item in menuItems'
        :key='item.name'
        :to='item.path'
      )
        v-icon(left) {{ item.icon }}
        | {{ item.name }}
    v-spacer
    // TODO:
    // Check if user is logged in and either show this or their username
    v-toolbar-items
      v-btn(flat to='/login') LOG IN
      v-btn(flat to='/signup') SIGN UP
</template>

<script>

export default {
  data() {
    return {
      title: 'CliO-Vis',
      menuItems: [
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
};
</script>

<style scoped>
</style>

