import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import colors from 'vuetify/es5/util/colors';

Vue.use(Vuetify, {
  theme: {
    primary: '#363640',
    secondary: colors.grey.lighten4,
    accent: colors.lime.lighten3,
  },
});
