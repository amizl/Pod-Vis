import Vue from 'vue';
import Router from 'vue-router';
import { requireAuth, requireNotAuth } from './authGuards';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      beforeEnter: requireAuth,
    },
    {
      path: '/cohorts',
      name: 'cohortManager',
      component: () => import('@/views/CohortManager.vue'),
      beforeEnter: requireAuth,
    },
    {
      path: '/cohorts/build',
      name: 'buildCohort',
      component: () => import('@/views/BuildCohort.vue'),
      beforeEnter: requireAuth,
      props: route => ({
        id: route.query.id,
      }),
    },
    {
      path: '/:user/explore/:dataset/:analysis',
      name: 'dataExplorer',
      component: () => import('@/views/DataExplorer.vue'),
      beforeEnter: requireAuth,
    },
    {
      path: '/analysis',
      // path: '/:user/analysis/:dataset/:analysis',
      name: 'analysis',
      component: () => import('@/views/AnalysisTool.vue'),
      beforeEnter: requireAuth,
      props: route => ({
        user: route.params.user,
        dataset: route.params.dataset,
        analysis: route.params.analysis,
      }),
    },
    {
      path: '/datasets',
      name: 'datasetManager',
      component: () => import('@/views/DatasetManager.vue'),
      beforeEnter: requireAuth,
      // children: [
      //   {
      //     path: 'build',
      //     component: () => import('@/views/BuildDataset.vue'),
      //   },
      // ],
    },
    {
      path: '/datasets/build',
      name: 'buildDataset',
      component: () => import('@/views/BuildDataset.vue'),
      props: route => ({
        id: route.query.id,
      }),
    },
    {
      path: '/datasets/:id',
      name: 'dataset',
      component: () => import('@/views/Dataset.vue'),
      props: route => ({
        id: route.params.id,
      }),
    },
    {
      path: '/signin',
      name: 'signIn',
      component: () => import('@/views/SignIn.vue'),
      beforeEnter: requireNotAuth,
    },
    // Routes for testing componenets
    {
      path: '/test',
      name: 'test',
      component: () => import('@/views/Test.vue'),
      children: [
        {
          path: 'heatmap',
          component: () =>
            import('@/components/charts/HierarchicalHeatmap.vue'),
        },
        {
          path: 'auth',
          component: () => import('@/components/auth/UserAuthentication.vue'),
        },
        {
          path: 'table',
          component: () =>
            import('@/components/DatasetManager/DatasetTable.vue'),
        },
        {
          path: 'bar',
          // component: () => import('../components/charts/BarChart.vue'),
        },
        {
          path: 'stackedbar',
          // component: () => import('../components/charts/StackedBarChart.vue'),
        },
        {
          path: 'loading',
          component: () => import('@/components/common/LoadingSpinner.vue'),
        },
        {
          path: 'cohortCard',
          component: () => import('@/components/CohortManager/CohortCard.vue'),
        },
        {
          path: 'categoricalCard',
          component: () =>
            import('@/components/CohortManager/CategoricalCard.vue'),
        },
        {
          path: 'testCharts',
          component: () => import('@/views/TestCharts.vue'),
        },
      ],
    },
  ],
});
