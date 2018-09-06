import Vue from 'vue';
import Router from 'vue-router';
import Home from '../views/Home.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/cohortManager',
      name: 'cohortManager',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () =>
        import('../views/CohortManager.vue'),
    },
    {
      path: '/dataExplorer',
      name: 'dataExplorer',
      component: () =>
        import('../views/DataExplorer.vue'),
    },
    {
      path: '/analysisTool',
      name: 'analysisTool',
      component: () =>
        import('../views/AnalysisTool.vue'),
    },
    {
      path: '/datasetManager',
      name: 'datasetManager',
      component: () =>
        import('../views/DatasetManager.vue'),
    },
  ],
});
