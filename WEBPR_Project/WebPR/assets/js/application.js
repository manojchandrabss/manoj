/* globals $, _, alertify */
'use strict';

/**
 * application core module
 *
 * @version 1.0
 *
 */
var APP = (function($, _, alertify) {
  // definex exportable methods of the module
  var exports = {};

  /**
   * messaging  bus
   * @namespace
   */
  exports.msg = {

    /**
     * display message using alertify library
     *
     * @param {object} msgObject the message object representing type and text
     *    of the message
     * @param {string} msgObject.TYPE type of the message
     *    (like success | error | warning etc)
     * @param {string} msgObject.MESSAGE text of the message to be displayed
     * @returns {void}
     */
    show: function(msgObject) {
      alertify[msgObject.TYPE](msgObject.MESSAGE);
    },
    success: function(message) {
      this.show({
        TYPE: 'success',
        MESSAGE: message
      });
    },
    error: function(message) {
      this.show({
        TYPE: 'error',
        MESSAGE: message
      });
    }
  };

  /**
   * toggle spinner for the container
   *
   * `waitable` is element that has class `.waitable` and been able to
   * has spinner while data is loading.
   *
   * @returns {undefined}
   */
  exports.spinner = {
    show: function(waitable) {
      waitable.addClass('waiting');
    },
    hide: function(waitable) {
      waitable.removeClass('waiting');
    },
    toggle: function(container) {
      var waitable = container.find('.waitable');

      if (waitable.hasClass('waiting')) {
        this.hide(waitable);
      } else {
        this.show(waitable);
      }
    }
  };

  /**
   * function for getting filter data for charts.
   *
   * @returns {object} JSON that contains `query`, `type`, `date` and
   *                   `period` params that required for dashboard charts.
   */
  exports.getFilterParams = function() {
    var query = $('#merchant_search').val(),
      // get keyword's dict form a `keywords` array, it is needing for
      // resolving a type of keyword
      keyword = keywords.filter(function(keyword) {
        return keyword.value === query;
      })[0],
      keywordType = '',
      keywordQuery = '';

    if (keyword) {
      keywordType = keyword.type;
      keywordQuery = keyword.query;
    }

    return {
      'filter': keywordQuery,
      'keywordType': keywordType,
      'date': $('#current_date').html(),
      'period': $('#toggle_period').children('.active').data('period')
    };
  };

  /**
   * show messages those stored in template.
   *
   * @returns {void}
   */
  exports.showMessages = function() {
    var $messages = $('.alert'),
      maxMessagesCount = 5;

    if ($messages.length > maxMessagesCount) {
      return;
    }

    _.each($messages, function(e, s) {
      exports.msg.success($('#message' + s).text().trim());
    });
  };

  /**
   * init the module
   *
   * @returns {void}
   */
  exports.init = function() {
    // count of max messages on a display
    var maxLogItems = 5;
    // define interpolation marks for string templates
    _.templateSettings = {
      interpolate: /\{(.+?)\}/g
    };
    // define standard position for message
    alertify.logPosition('top right');
    alertify.maxLogItems(maxLogItems);
    // show stored messages
    exports.showMessages();
    // set up custom autocomplete widget
    $.widget('custom.customAutoComplete', $.ui.autocomplete, {
      _create: function() {
        this._super();
        this.widget().menu('option', 'items',
                            '> :not(.ui-autocomplete-type)');
      },
      _renderItem: function(ul, item) {
        return $('<li></li>').data('item.autocomplete', item)
                             .append('<a>' + item.label + '</a>')
                             .appendTo(ul);
      }
    });
    // init Bootstrap tooltips
    $(function() {
      $('[data-toggle="tooltip"]').tooltip();
    });
  };

  return exports;
}($, _, alertify));

APP.init();
