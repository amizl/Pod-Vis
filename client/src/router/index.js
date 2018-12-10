import Vue from 'vue';
import Router from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import AuthGuard from './authGuard';

Vue.use(Router);

export default new Router({
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
      path: '/cohortManager',
      name: 'cohortManager',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/CohortManager.vue'),
      beforeEnter: AuthGuard,
    },
    {
      path: '/dataExplorer',
      name: 'dataExplorer',
      component: () => import('../views/DataExplorer.vue'),
      beforeEnter: AuthGuard,
    },
    {
      path: '/analysisTool',
      name: 'analysisTool',
      component: () => import('../views/AnalysisTool.vue'),
      beforeEnter: AuthGuard,
    },
    {
      path: '/datasetManager',
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
      path: '/datasetManager/build',
      name: 'buildDataset',
      component: () => import('@/views/BuildDataset.vue'),
      props: route => ({
        id: route.query.id,
      }),
    },
    {
      path: '/datasetManager/dataset/:id',
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
          component: () => import('@/components/charts/HierarchicalHeatmap.vue'),
        },
        {
          path: 'auth',
          component: () => import('../components/auth/UserAuthentication.vue'),
        },
        {
          path: 'table',
          component: () => import('../components/DatasetManager/DatasetTable.vue'),
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
          component: () => import('@/components/CohortManager/CategoricalCard.vue'),
        },
        {
          path: 'testCharts',
          component: () => import('@/views/TestCharts.vue'),
        },
      ],
    },
  ],
});
