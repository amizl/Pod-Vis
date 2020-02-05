<template>
  <rect
    :x="x"
    :y="useTweeningYIfNotFalsy"
    :width="width"
    :height="useTweeningHeightIfNotFalsy"
    :fill="fill"
    ><title v-if="tooltip !== ''">{{ tooltip }}</title></rect
  >
</template>

<script>
import TWEEN from '@tweenjs/tween.js';

export default {
  props: {
    x: {
      type: Number,
      required: true,
    },
    y: {
      type: Number,
      required: true,
      default: 0,
    },
    // ystart: {
    //   type: Number,
    //   required: true,
    //   default: 0,
    // },
    width: {
      type: Number,
      required: true,
    },
    height: {
      type: Number,
      required: true,
      default: 0,
    },
    fill: {
      type: String,
      required: true,
    },
    tooltip: {
      type: String,
      required: false,
      default: '',
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
      // let frameHandler;

      // // Handles updating the tween on each frame.
      // const animate = function() {
      //   if (TWEEN.update()) {
      //     frameHandler = requestAnimationFrame(animate);
      //   }
      // };

      new TWEEN.Tween({ tweeningValue: startValue })
        .to({ tweeningValue: endValue }, 500)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onUpdate(({ tweeningValue }) => {
          this[prop] = tweeningValue;
        })
        .onComplete(() => {
          // Make sure to clean up after ourselves.
          // cancelAnimationFrame(frameHandler);
        })
        .start();
      // frameHandler = requestAnimationFrame(animate);
    },
  },
};
</script>

<style scoped>
rect {
  cursor: pointer;
}
</style>
