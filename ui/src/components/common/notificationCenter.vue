<template>
  <v-snackbar
    v-if="notification"
    v-model="notifyState"
    :color="notification.type"
    bottom
  >
    {{ notification.message }}
    <!-- <v-btn color="white" flat @click="notify"> Close </v-btn> -->
  </v-snackbar>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/notifications/types';

export default {
  computed: {
    ...mapState('notifications', {
      notification: state.NOTIFICATION,
      _notify: state.NOTIFY,
    }),
    notifyState: {
      get() {
        return this._notify;
      },
      set() {
        this.notify();
      },
    },
  },
  methods: {
    ...mapActions('notifications', {
      notify: actions.NOTIFY,
    }),
  },
};
</script>

<style scoped></style>d
