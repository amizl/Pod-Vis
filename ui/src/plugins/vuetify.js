import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import colors from 'vuetify/es5/util/colors';

Vue.use(Vuetify, {
  theme: {
    themes: {
      light: {
        primary: colors.indigo,
        accent: colors.indigo,
        background: colors.indigo.lighten5,
        'v-divider': colors.indigo.lighten5,
      },
    },
  },
});

export default new Vuetify({
  icons: {
    iconfont: 'mdi',
  },
});
