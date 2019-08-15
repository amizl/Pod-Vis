<template>
  <rect v-if="!mounted" v-bind="$attrs" :y="y" :height="height" />
  <rect
    v-else
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
      mounted: false,
      timeout: 500,
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
  mounted() {
    // Small hack to wait until the initial tween values
    // get to their starting values and then toggle our
    // animated rect.
    setTimeout(() => {
      this.mounted = true;
    }, this.timeout);
  },
  methods: {
    /**
     * Method to tween from one value to another
     */
    tween(startValue, endValue, prop) {
      // let frameHandler;

      // // Handles updating the tween on each frame.
      // const animate = function(currentTime) {
      //   TWEEN.update(currentTime);
      //   frameHandler = requestAnimationFrame(animate);
      // };
      new TWEEN.Tween({ tweeningValue: startValue })
        .to({ tweeningValue: endValue }, this.timeout)
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
