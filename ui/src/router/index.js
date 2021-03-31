import Vue from 'vue';
import Router from 'vue-router';
import { requireAuth, requireNotAuth } from './authGuards';
import { logEvent } from '@/utils/logging';

Vue.use(Router);

const router =  new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/homepage',
    },
    {
      path: '/homepage',
      name: 'homepage',
      component: () => import('@/views/Dashboard.vue'),
      beforeEnter: requireAuth,
    },
    {
      path: '/data_summary',
      name: 'dataSummary',
      component: () => import('@/views/DataSummary.vue'),
      beforeEnter: requireAuth,
      props: route => ({
        collectionId: +route.query.collection,
      }),
    },
    {
      path: '/study_datasets',
      name: 'studyDataset',
      component: () => import('@/views/StudyDatasets.vue'),
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
      path: '/explore',
      name: 'dataExplorer',
      component: () => import('@/views/DataExplorer.vue'),
      beforeEnter: requireAuth,
      props: route => ({
        collectionId: +route.query.collection,
        variableId: +route.query.variable,
        cohortIds: route.query.cohorts,
        visibleCohortIds: route.query.visibleCohorts,
      }),
    },
    {
      path: '/summary',
      name: 'summary',
      component: () => import('@/views/AnalysisSummary.vue'),
      beforeEnter: requireAuth,
      props: route => ({
        user: route.params.user,
        collectionId: +route.query.collection,
        cohortIds: route.query.cohorts,
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
        id: +route.params.id,
      }),
      beforeEnter: requireAuth,
    },
    {
      path: '/study_datasets/:id',
      name: 'study_dataset',
      component: () => import('@/views/StudyDataset.vue'),
      props: route => ({
        id: +route.params.id,
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

router.beforeEach((to, from, next) => {
    logEvent(from.fullPath, to.fullPath, 'pageview', 'navigation', to.name);
    next();
});

export default router;
