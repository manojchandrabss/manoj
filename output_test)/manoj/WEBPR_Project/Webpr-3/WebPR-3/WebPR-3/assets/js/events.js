/* exported EVENTS */
'use strict';

/**
 *  application events
 *  reworked: https://davidwalsh.name/pubsub-javascript
 *  @module EVENTS
 *  @version 1.0
 *
 */
var EVENTS = (function() {

  // defines exportable methods of the module
  var exports = {},
    topics = {},
    hOP = topics.hasOwnProperty;

  /**
   * subscribe to event
   * @param {string} topic event's name to subscribe to
   * @param {function} listener that should get invoked once event is
   *     published / fired
   * @return {object} returns object representing params mapping
   */
  exports.subscribe = function(topic, listener) {
    // create the topic's object if not yet created
    if (!hOP.call(topics, topic)) {
      topics[topic] = [];
    }

    // add the listener to queue
    var index = topics[topic].
    push(listener) - 1;

    // provide handle back for removal of topic
    return {
      remove: function() {
        delete topics[topic][index];
      }
    };
  };

  /**
   * publish/fire event
   * @param {string} topic event's name being published/fired
   * @param {object} info data passed with event as object
   * @return {undefined}
   */
  exports.publish = function(topic, info) {
    // if the topic doesn't exist, or there's no listeners in queue,
    // just leave
    if (!hOP.call(topics, topic)) {
      return;
    }

    // cycle through topics queue, fire!
    topics[topic].
    forEach(function(item) {
      item(info !== undefined ? info : {});
    });
  };

  return exports;
}());
