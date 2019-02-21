import Vue from 'vue';
import Router from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import AuthGuard from './authGuard';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
      beforeEnter: AuthGuard,
    },
    {
      path: '/dashboard',
      name: 'home',
      component: Dashboard,
      beforeEnter: AuthGuard,
    },
    {
      path: '/cohorts/',
      name: 'cohortManager',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/CohortManager.vue'),
      beforeEnter: AuthGuard,
    },
    {
      path: '/cohorts/build',
      name: 'buildCohort',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/BuildCohort.vue'),
      beforeEnter: AuthGuard,
      props: route => ({
        id: route.query.id,
      }),
    },
    {
      path: '/:user/explore/:dataset/:analysis',
      name: 'dataExplorer',
      component: () => import('../views/DataExplorer.vue'),
      beforeEnter: AuthGuard,
    },
    {
      path: '/analysis',
      // path: '/:user/analysis/:dataset/:analysis',
      name: 'analysis',
      component: () => import('../views/AnalysisTool.vue'),
      beforeEnter: AuthGuard,
      props: route => ({
        user: route.params.user,
        dataset: route.params.dataset,
        analysis: route.params.analysis,
      }),
    },
    {
      path: '/datasets',
      name: 'datasetManager',
      component: () => import('../views/DatasetManager.vue'),
      beforeEnter: AuthGuard,
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
      component: () => import('../views/SignIn.vue'),
    },
    // Routes for testing componenets
    {
      path: '/test',
      name: 'test',
      component: () => import('../views/Test.vue'),
      children: [
        {
          path: 'heatmap',
          component: () =>
            import('@/components/charts/HierarchicalHeatmap.vue'),
        },
        {
          path: 'auth',
          component: () => import('../components/auth/UserAuthentication.vue'),
        },
        {
          path: 'table',
          component: () =>
            import('../components/DatasetManager/DatasetTable.vue'),
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
          component: () => import('../components/common/LoadingSpinner.vue'),
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
