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
    :x="useTweeningXIfNotFalsy"
    :width="useTweeningWidthIfNotFalsy"
  />
</template>

<script>
import TWEEN from '@tweenjs/tween.js';

export default {
  props: {
    width: {
      type: Number,
      required: true,
      default: 0,
    },
    x: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      tweeningWidth: 0,
      tweeningX: 0,
    };
  },
  computed: {
    /**
     * We only want to use tweening variable after the bar is already
     * drawn with the Y variable
     */
    useTweeningXIfNotFalsy() {
      return this.tweeningX ? this.tweeningX : this.x;
    },
    /**
     * We only want to use tweening variable after the bar is already
     * drawn with the Y variable
     */
    useTweeningWidthIfNotFalsy() {
      return this.tweeningWidth ? this.tweeningWidth : this.width;
    },
  },
  watch: {
    width(newValue, oldValue) {
      // When the height changes, tween from the old value to the new
      this.tween(oldValue, newValue, 'tweeningWidth');
    },
    x(newValue, oldValue) {
      // When the Y changes, tween from the old value to the new
      this.tween(oldValue, newValue, 'tweeningX');
    },
  },
  methods: {
    /**
     * Method to tween from one value to another
     */
    tween(startValue, endValue, prop) {
      // let frameHandler;

      // Handles updating the tween on each frame.
      // const animate = function(currentTime) {
      //   TWEEN.update(currentTime);
      //   frameHandler = requestAnimationFrame(animate);
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
