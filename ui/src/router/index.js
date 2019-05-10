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
      props: route => ({
        collectionId: +route.query.collection,
      }),
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
      path: '/explore',
      // path: '/:user/explore/:dataset/:analysis',
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
      beforeEnter: requireAuth,
    },
    {
      path: '/datasets/:id',
      name: 'dataset',
      component: () => import('@/views/Dataset.vue'),
      props: route => ({
        id: route.params.id,
      }),
      beforeEnter: requireAuth,
    },
    {
      path: '/signin',
      name: 'signIn',
      component: () => import('@/views/SignIn.vue'),
      beforeEnter: requireNotAuth,
    },
  ],
});
