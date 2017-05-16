/* exported TOOLS */
'use strict';

/**
 * tools for works with strings.
 *
 * @version 1.0
 */

var TOOLS = (function() {
  // define exportable methods of the module
  var exports = {};

  /**
   * truncate string and adds three dots if too long.
   *
   * @param {string} string - a string that you want to truncate.
   * @param {number} maxLength - lenght of the string that you want to truncate.
   * @returns {string} a truncated string.
   */
  exports.truncatechars = function(string, maxLength) {
    var defaultLength = 24,
      length = maxLength ? maxLength : defaultLength;

    if (string.length > length) {
      return string.substr(0, length) + '...';
    }

    return string;
  };

  /**
   * unescape unicode string.
   *
   * @param {string} value - decoded in unicode string.
   * @returns {string} unescape string.
   */
  exports.unescapeUnicode = function(value) {
    return unescape(
      value.toString().replace(/\\u([\d\w]{4})/gi, function(match, grp) {
        return String.fromCharCode(parseInt(grp, 16));
      })
    );
  };

  /**
   * returns array with random values.
   *
   * @param {number} length Length of the random array.
   * @param {number} max A max value of the random array.
   * @returns {Array} array with random numbers.
   */
  exports.randomArray = function(length, max) {
    var DEFAULT_LENGTH = 10,
      DEFAULT_MAX = 100,
      maxLength = typeof length !== 'undefined' ? length : DEFAULT_LENGTH,
      maxNum = typeof max !== 'undefined' ? max : DEFAULT_MAX;

    return Array.apply(Object, Array(maxLength)).map(function() {
      return Math.round(Math.random() * maxNum);
    });
  };

  /**
   * generate random color HEX code
   *
   * @returns {string} HEX code.
   */
  exports.getRandomColor = function() {
    var numeral = 16,
      start = 2,
      end = 8;

    return '#' + (Math.random().toString(numeral)).slice(start, end);
  };

  /**
   * generate array of random HEX colors
   *
   * @param {number} length - length of the array.
   * @returns {array} array of HEX colors.
   */
  exports.getRandomColors = function(length) {
    return Array.apply(Object, Array(length)).map(function() {
      return exports.getRandomColor();
    });
  };

  return exports;
}());
