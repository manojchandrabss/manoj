/* globals $ */
/* exported Popover, MentionDetailView, TodoDetailView, TodoCreate,
   setRangeDisplay */
'use strict';

/**
 * control of Popover actions
 * @namespace
 */
var Popover = (function($) {
  // definex exportable methods of the module
  var exports = {};

  /**
   * function for open popover and append content to this
   *
   * @param {string} popover - Popover caller
   * @param {string} placement - Popover placement(top, bottom, left, right)
   * @param {string} container - Popover container
   * @returns {undefined}
   */
  exports.open = function(popover, placement, container) {
    $(popover).popover({
      html: true,
      placement: placement,
      trigger: 'manual',
      content: function() {
        return $(this).closest('.block-buttons').find(container)
                      .html();
      }
    });
    $(popover).popover('show');
  };

  /**
   * close the popover (destroy)
   *
   * @param {string} popover - Popover container
   * @returns {undefined}
   */
  exports.close = function(popover) {
    $(popover).popover('destroy');
  };

  return exports;
}($));

/**
 * function to show modal view with mentions details in merchant dashboard
 *
 * @param {object} mention - a DOM element
 * @returns {undefined}
 */
function MentionDetailView(mention) {
  var id = $(mention).attr('id');

  $('#mention_text').html($('#mention_full_text' + id).text());
  $('#mention_link').attr('href', $('#mention_link_list' + id).attr('href'));
}

/**
 * function to show modal view with to-do details in merchant dashboard
 *
 * @param {object} todo - a DOM element
 * @returns {void}
 */
function TodoDetailView(todo) {
  var id = $(todo).attr('id');

  $('#detail_comment').html($('#todo_detail' + id).html());
}

/**
 * function for sets data for display date range and widgets, calculates
 * date ranges using `moment.js` and starts update widgets for the choosen
 * range and date.
 *
 * @param {function} clbk - Callback function;
 * @returns {boolean} false
 */
function setRangeDisplay(clbk) {
  var dateStartStr = $('#current_date').text(),
    dateStart = null,
    dateEnd = null,
    datePrev = null,
    dateNext = null,
    periodStr = $('#toggle_period .active').data('period'),
    inputFormat = 'DD MM YY',
    outputFormat = 'MMM DD, YYYY',
    date = moment(dateStartStr, inputFormat),
    settings = {
      week: {
        label: 'isoweek', // for starts week from monday
        range: 'days',
        count: 7
      },
      month: {
        label: 'month',
        range: 'months',
        count: 1
      }
    };

  // returns false if date and selected period are not valid
  if (!date.isValid() && !(['week', 'month'].indexOf(periodStr) >= 0)) {
    return false;
  }
  // sets start and end of date interval using selected params and
  // settings dict
  dateStart = date.clone().startOf(settings[periodStr].label);
  dateEnd = date.clone().endOf(settings[periodStr].label);
  datePrev = dateStart.clone().subtract(settings[periodStr].count,
                                        settings[periodStr].range);
  dateNext = dateEnd.clone().add(settings[periodStr].count,
                                 settings[periodStr].range);
  // sets data fro date togglers (arrows `prev` and `next`)
  $('#date_toggle [data-direction=prev]').attr('data-date',
                                               datePrev.format(inputFormat));
  $('#date_toggle [data-direction=next]').attr('data-date',
                                               dateNext.format(inputFormat));
  // sets range displays
  $('#date_range').html(
    dateStart.format(outputFormat) + ' - ' +
    dateEnd.format(outputFormat)
  );

  if (typeof clbk !== 'undefined') {
    clbk();
  }

  return false;
}
