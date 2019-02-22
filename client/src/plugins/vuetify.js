import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import colors from 'vuetify/es5/util/colors';

Vue.use(Vuetify, {
  theme: {
    primary: colors.grey.darken4,
    background: colors.grey.lighten5,
  },
  // theme: {
  //   // primary: '#212B3A',
  //   primary: '#035388',
  //   // primary: '#2c3e50',
  //   // primary: '#013852',
  //   // primary: '#2C384A',
  //   secondary: '#2BB0ED',
  //   accent: '#282F3C',
  //   background: '#F0F4F8',
  //   // background: '#F5F7FA',
  //   // background: '#E4E7EB',
  //   iconColor: '#99a4ae',
  //   foo: '#9FB3C8',
  //   fooo: '#9AA5B1',
  // },
});
