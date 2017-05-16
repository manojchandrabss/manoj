/* globals $, _ */
/* exported Tracker */
'use strict';

/**
 * tracker managing module.
 *
 * @namespace
 */
var Tracker = (function($, _) {
  // define exportable methods of the module
  var exports = {};

  /**
   * a success callback for change tracker's options form.
   *
   * @param {object} data A JSON object from server.
   * @param {status} status Status text.
   * @param {object} xhr The XHR object.
   * @param {object} form The AjaxForm object.
   * @returns {undefined}
   */
  function _successCallback(data, status, xhr, form) {
    var tracker = form.closest('.tracker'),
      panelTitleTemplate = _.template('<a href="{ url }">{ title }</a>');
    form.find('.error').remove();
    // set new urlize merchant title in column header.
    tracker.find('.panel-heading > h4')
      .html(panelTitleTemplate({
        url: data.url,
        title: data.merchant
      }));
    // storing a tracker ID for update.
    tracker.attr('data-id', data.pk);
    // close popover
    Tracker.closeSettings();
    // update list
    Tracker.getMentions(data.pk, 1);
  }

  /**
   * an error callback for change tracker's options form.
   *
   * @param {object} data A JSON object from server.
   * @returns {undefined}
   */
  function _errorCallback(data) {
    var form = $('#tracker_add_id'),
      errorTemplate = _.template(
        '<span class="help-block error"><strong>{ text }</strong></span>');
    // drop old messages.'<span class="help-block error"><strong>' +
    form.find('.help-block.error').remove();
    // add django form messages.
    $.each($.parseJSON(data.responseText), function(k, v) {
      $(errorTemplate({
        text: v
      })).insertAfter(form.find('#id_' + k));
      form.find('#div_id_' + k).addClass('has-error');
    });
  }

  /**
   * an error callback for change tracker's options form.
   *
   * @param {number} trackerId A Tracker's ID.
   * @param {object} form A default form object.
   * @returns {string|object} form The form HTML with errors or JSON.
   */
  function _getForm(trackerId, form) {
    var defaultForm = form,
      options = {
        cache: false
      };
    // get updated form for created tracker.
    if (trackerId) {
      options.url = '/tracker/' + trackerId + '/update';
      defaultForm = $.get(options);
    }
    return defaultForm;
  }

  /**
   * add new Tracker HTML into trackers list.
   *
   * @returns {undefined}
   */
  exports.add = function() {
    // a new tracker's HTML is storeing inside the template
    // with a '.hidden' class.
    var newTracker = $('.panel.hidden').clone().removeClass('hidden');

    $('.block-horizontal-scroll').prepend(newTracker);
    // hide all opened dialogs.
    Tracker.closeSettings();
  };

  /**
   * remove a Tracker for the trackers list.
   *
   * @param {object} button a DOM element.
   * @returns {undefined}
   */
  exports.remove = function(button) {
    var tracker = $(button).closest('.tracker');

    tracker.remove();
    // delete tracker from DB
    if (tracker.data('id')) {
      $.get('/tracker/' + tracker.data('id') + '/delete');
    }
  };

  /**
   * save current tracker's settings if exists, else will create a new tracker.
   *
   * @param {object} button a DOM element.
   * @returns {undefined}
   */
  exports.save = function(button) {
    var form = $(button).parent(),
      tracker = $(button).closest('.tracker'),
      // the ID is a tracker ID that stored for updating the tracker.
      id = tracker.data('id') ? tracker.data('id') : null,
      // set url that will be use, create or update a tracker.
      url = id ? '/tracker/' + id + '/update' : '/tracker/create',
      options = {
        success: _successCallback,
        error: _errorCallback,
        type: 'POST',
        dataType: 'json',
        url: url
      };
    // submiting the form and having fun.
    form.ajaxSubmit(options);
  };

  /**
   * show or hide a dialog of the tracker settings.
   *
   * @param {object} button a DOM element.
   * @returns {undefined}
   */
  exports.toggleSettings = function(button) {
    var tracker = $(button).closest('.tracker'),
      trackerId = tracker.data('id') ? tracker.data('id') : null,
      form = $(button).closest('.tracker')
      .find('.form-wrapper')
      .html();

    if (!$(button).hasClass('has-popover')) {
      Tracker.closeSettings();
      // getting and inserting an updated tracker form.
      $.when(_getForm(trackerId, form)).done(function(form) {
        // popover shows if has no class .has-popover.
        $(button).popover({
          html: true,
          placement: 'bottom',
          trigger: 'manual',
          content: function() {
            return form;
          }
        });
        $(button).addClass('has-popover');
        $(button).popover('show');
      });
    }
  };

  /**
   * hide all dialogs which were opened.
   *
   * @returns {undefined}
   */
  exports.closeSettings = function() {
    $('.tracker').find('.settings.has-popover').removeClass('has-popover');
    $('.tracker').find('.popover').popover('destroy');
  };

  /**
   * get updated mentions list and paginate it.
   *
   * @param {number} trackerId The tracker's ID.
   * @param {number} page A page number for pagination.
   * @returns {undefined}
   */
  exports.getMentions = function(trackerId, page) {
    var data = null,
      tracker = $('.tracker[data-id=' + trackerId + ']'),
      url = 'tracker/' + trackerId + '/mentions?page=' + page;
    // drop previous mentions if this has called, but it is not pagination.
    if (parseInt(page, 10) === 1) {
      tracker.find('.list-group-item').remove();
    }

    $.get(url, function(responseData) {
      data = responseData;
      // set message for an empty list
      if (!data) {
        data = '<div class="list-group-item text-center note">' +
          'No results</div>';
      }
      tracker.find('.list-group').append(data);
      // set page number. If is paginated, it will be current page number.
      tracker.attr('data-page', page);
    });
  };

  /**
   * scroll event listener.
   *
   * @param {element} element An element that will have the event.
   * @returns {undefined}
   */
  exports.scrollListener = function(element) {
    var tracker = $(element).closest('.tracker'),
      height = tracker.find('.list-group').height() - $(element).height(),
      page = parseInt(tracker.attr('data-page'), 10);
    // if scroll and height are equal or more - get data.
    if ($(element).scrollTop() >= height) {
      Tracker.getMentions(tracker.data('id'), page + 1);
    }
  };

  return exports;
}($, _));
