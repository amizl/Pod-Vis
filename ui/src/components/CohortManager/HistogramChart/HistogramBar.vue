<template>
  <!-- <rect
    :x="x"
    :y="useTweeningYIfNotFalsy"
    :width="width"
    :height="useTweeningHeightIfNotFalsy"
    :fill="fill"
  ></rect> -->
  <rect
    v-bind="$attrs"
    :y="useTweeningYIfNotFalsy"
    :height="useTweeningHeightIfNotFalsy"
  />
</template>

<script>
import TWEEN from '@tweenjs/tween.js';

export default {
  props: {
    height: {
      type: Number,
      required: true,
      default: 0,
    },
    y: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      tweeningHeight: 0,
      tweeningY: 0,
    };
  },
  computed: {
    /**
     * We only want to use tweening variable after the bar is already
     * drawn with the Y variable
     */
    useTweeningYIfNotFalsy() {
      return this.tweeningY ? this.tweeningY : this.y;
    },
    /**
     * We only want to use tweening variable after the bar is already
     * drawn with the Y variable
     */
    useTweeningHeightIfNotFalsy() {
      return this.tweeningHeight ? this.tweeningHeight : this.height;
    },
  },
  watch: {
    height(newValue, oldValue) {
      // When the height changes, tween from the old value to the new
      this.tween(oldValue, newValue, 'tweeningHeight');
    },
    y(newValue, oldValue) {
      // When the Y changes, tween from the old value to the new
      this.tween(oldValue, newValue, 'tweeningY');
    },
  },
  methods: {
    /**
     * Method to tween from one value to another
     */
    tween(startValue, endValue, prop) {
      new TWEEN.Tween({ tweeningValue: startValue })
        .to({ tweeningValue: endValue }, 500)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onUpdate(({ tweeningValue }) => {
          this[prop] = tweeningValue;
        })
        .start();
    },
  },
};
</script>

<style scoped>
rect {
  cursor: pointer;
}
</style>
