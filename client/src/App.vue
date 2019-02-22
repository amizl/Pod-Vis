<template>
  <v-app>
    <app-side-bar v-if="isUserAuthenicated"></app-side-bar>
    <!-- <v-system-bar
      app
      dark
      status
      color="primary darken-3"
      height="10px"
    ></v-system-bar> -->
    <!-- <app-header v-if="isUserAuthenicated" app></app-header> -->
    <v-content class="background">
      <transition name="fade" mode="out-in">
        <router-view></router-view>
      </transition>
    </v-content>
  </v-app>
</template>
<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/auth/types';
import Footer from './components/layout/Footer.vue';
import SideBar from './components/layout/Sidebar.vue';
import Header from './components/layout/Header.vue';
import SignIn from './views/SignIn.vue';

export default {
  name: 'App',
  components: {
    appFooter: Footer,
    signInForm: SignIn,
    appSideBar: SideBar,
    appHeader: Header,
  },
  data() {
    return {};
  },
  computed: {
    ...mapState('auth', {
      user: state.USER,
    }),
    isUserAuthenicated() {
      return this.user !== null && this.user !== undefined;
    },
  },
  watch: {},
  created() {
    this.redirectUserIfNotAuth();
  },
  methods: {
    redirectUserIfNotAuth() {
      if (!this.isUserAuthenicated) {
        this.$router.push('/signin');
      }
    },
  },
};
</script>

<style lang="stylus">
.fade-enter-active,
.fade-leave-active {
  transition-duration: 0.3s;
  transition-property: opacity;
  transition-timing-function: ease;
}
.fade-enter,
.fade-leave-active {
  opacity: 0;
}

// @require '../node_modules/vuetify/src/stylus/settings/_colors.styl'
// $material-light := {
//   status-bar: {
//     regular: #E0E0E0,
//     lights-out: rgba(#fff, .7)
//   },
//   app-bar: #F5F5F5,
//   background: #FAFAFA,
//   cards: #FFFFFF,
//   chips: {
//     background: $grey.lighten-2,
//     color: rgba(#000, .87)
//   },
//   dividers: rgba(217, 226, 236, 1),
//   text: {
//     theme: #fff,
//     primary: rgba(#000, .87),
//     secondary: rgba(#000, .54),
//     disabled: rgba(#000, .38),
//     link: $blue.darken-2,
//     link-hover: $grey.darken-3
//   },
//   icons: {
//     active: rgba(159, 179, 200, 1),
//     inactive: rgba(217, 226, 236, 1)
//   },
//   inputs: {
//     box: rgba(#000, .04),
//     solo-inverted: rgba(#000, .16),
//     solo-inverted-focused: #424242,
//     solo-inverted-focused-text: #fff
//   },
//   buttons: {
//     disabled: rgba(#000, .26),
//     focused: rgba(#000, .12),
//     focused-alt: rgba(#fff, .6),
//     pressed: rgba(#999, .4)
//   },
//   expansion-panels: {
//     focus: #EEEEEE
//   },
//   list-tile: {
//     hover: rgba(240, 244, 248, 1)
//   },
//   selection-controls: {
//     thumb: {
//       inactive: $grey.lighten-5,
//       disabled: $grey.lighten-1
//     },
//     track: {
//       inactive: rgba(#000, .38),
//       disabled: rgba(#000, .12)
//     }
//   },
//   slider: {
//     active: rgba(#000, .38),
//     inactive: rgba(#000, .26),
//     disabled: rgba(#000, .26),
//     discrete: #000
//   },
//   tabs: {
//     active: rgba(#000, .87)
//   },
//   text-fields: {
//     box: rgba(#000, .06),
//     box-hover: rgba(#000, .12)
//   },
//   input-bottom-line: rgba(#000, .42),
//   stepper: {
//     active: rgba(#fff, 1),
//     completed: rgba(#000, 0.87),
//     hover: rgba(#000, 0.54)
//   },
//   table: {
//     active: $grey.lighten-4
//     hover: rgba(240, 244, 248, 1),
//   },
//   picker: {
//     body: #fff,
//     clock: $grey.lighten-2,
//     indeterminateTime: $grey.lighten-1,
//     title: $grey.lighten-2
//   },
//   bg-color: #fff
//   fg-color: #000
//   text-color: #000
//   primary-text-percent: .87
//   secondary-text-percent: .54
//   disabledORhints-text-percent: .38
//   divider-percent: .12
//   active-icon-percent: .54
//   inactive-icon-percent: .38
// }
// @require '../node_modules/vuetify/src/stylus/main.styl'
</style>
