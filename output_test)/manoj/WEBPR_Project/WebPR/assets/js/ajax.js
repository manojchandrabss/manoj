/* globals $, _, Cookies, CONFIG */
/* exported  AJAX */
'use strict';

/**
 *  ajax and api calls
 *  @module AJAX
 *  @version 1.0
 *
 */
var AJAX = (function($, _, Cookies, CONFIG) {

  // definex exportable methods of the module
  var exports = {};

  /**
   * checks if the HTTP method is safe for CSRF protection taken from
   * Django documentation site
   *
   * @param {string} method the HTTP method
   * @returns {bool} boolean
   */
  function _csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/).test(method);
  }

  /**
   * checks if the URL is from the same origin taken from Django
   * documentation site
   *
   * @param {string} url The first number.
   * @returns {bool} boolean
   */
  function _sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host, // host + port
      protocol = document.location.protocol,
      srOrigin = '//' + host,
      origin = protocol + srOrigin;
    // allow absolute or scheme relative URLs to same origin
    return url === origin ||
      url.slice(0, origin.length + 1) === origin + '/' ||
      url === srOrigin ||
      url.slice(0, srOrigin.length + 1) === srOrigin + '/' ||
      // or any other URL that isn't scheme relative or absolute i.e relative.
      !(/^(\/\/|http:|https:).*/).test(url);
  }

  /**
   * create merchant
   *
   * @param {object} merchant to be saved
   * @returns {ajax} jquery ajax promise
   */
  exports.createMerchant = function(merchant) {
    return $.ajax({
      url: CONFIG.MERCHANT_MANAGER + 'new',
      type: 'POST',
      data: merchant,
      dataType: 'json'
    });
  };

  /**
   * update merchant
   *
   * @param {object} merchant to be updated
   * @returns {ajax} jquery ajax promise
   */
  exports.updateMerchant = function(merchant) {
    return $.ajax({
      url: CONFIG.MERCHANT_MANAGER + merchant.id + '/update',
      type: 'POST',
      data: merchant,
      dataType: 'json'
    });
  };

  /**
   * create user for merchant
   *
   * @param {object} user to be saved
   * @returns {ajax} jquery ajax promise
   */
  exports.createUserForMerchant = function(user) {
    return $.ajax({
      url: CONFIG.USER_MANAGER + 'create_user',
      type: 'POST',
      data: user,
      dataType: 'json'
    });
  };

  /**
   * get mentions list for merchant
   *
   * @param {number} id - merchant ID.
   * @param {string} statusChoice - mentions status (`all`, `assigned`,
   *                 `unassigned`). Default is `all`.
   * @param {number} pageNumber - page number for pagination. Default is 1.
   * @returns {ajax} jquery ajax promise
   */
  exports.getMentionsForMerchant = function(id, statusChoice, pageNumber) {
    var data = {};

    data.mention_status = statusChoice ? statusChoice : 'all';
    data.page = pageNumber ? pageNumber : 1;

    return $.ajax({
      url: CONFIG.MERCHANT_MANAGER + id + '/mentions',
      type: 'GET',
      data: data
    });
  };

  /**
   * get todos list for merchant
   *
   * @param {number} id - merchant ID.
   * @param {string} statusChoice - todos status (`all`, `resolved`,
   *                 `unresolved`). Default is `all`.
   * @param {number} pageNumber - page number for pagination. Default is 1.
   * @returns {ajax} jquery ajax promise
   */
  exports.getTodosForMerchant = function(id, statusChoice, pageNumber) {
    var data = {};

    data.status = statusChoice ? statusChoice : 'all';
    data.todo = pageNumber ? pageNumber : 1;

    return $.ajax({
      url: CONFIG.MERCHANT_MANAGER + id + '/todos',
      type: 'GET',
      data: data
    });
  };

  /**
   * toggle status for todo
   *
   * @param {number} id - todo ID.
   * @returns {ajax} jquery ajax promise
   */
  exports.toggleTodoStatus = function(id) {
    return $.ajax({
      url: CONFIG.TODO_MANAGER + id + '/toggle_status',
      type: 'GET'
    });
  };

  /**
   * create todo for mention
   *
   * @param {object} todo to be saved
   * @returns {ajax} jquery ajax promise
   */
  exports.createTodoForMention = function(todo) {
    return $.ajax({
      url: CONFIG.MERCHANT_MANAGER + 'addtodo',
      type: 'POST',
      data: todo,
      dataType: 'json'
    });
  };

  /**
   * toggle flag for mention
   *
   * @param {object} params - params for URL.
   * @returns {ajax} jquery ajax promise
   */
  exports.mentionFlagToggle = function(params) {
    var data = {};

    return $.ajax({
      url: String(CONFIG.MERCHANT_MANAGER + params.merchantId +
                  '/mentions/' + params.mentionUId),
      type: 'GET',
      data: data,
      dataType: 'json'
    });
  };

  /**
   * get data for ISO`s Industrie`s complaints chart
   *
   * @param {object} params - params for filter
   * @returns {ajax} jquery ajax promise
   */
  exports.getDataForIndustriesComplaintsChart = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'industry_complaints_chart',
      type: 'GET',
      data: data,
      dataType: 'json'
    });
  };

  /**
   * get data for ISO`s Perfomance Tracking chart
   *
   * @param {object} params - params for filter
   * @returns {ajax} jquery ajax promise
   */
  exports.getDataForPerfomanceTrackingChart = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'score',
      type: 'GET',
      data: data,
      dataType: 'json'
    });
  };

  /**
   * get data for Mention chart
   *
   * @param {object} params - params for filter
   * @returns {ajax} jquery ajax promise
   */
  exports.getDataForMentionsChart = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'iso_mention_chart',
      type: 'GET',
      data: data,
      dataType: 'json'
    });
  };

  /**
   * get lowest ranked merchants for iso
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise
   */
  exports.getLowestRankedMerchants = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'lowest_ranked',
      type: 'GET',
      data: data
    });
  };

  /** get complaints for ISO
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise
   */
  exports.getComplaintsForISO = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'complaints',
      type: 'GET',
      data: data
    });
  };

  /** get response rate for ISO
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise
   */
  exports.getDataForResponseRateChart = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'response_rate_iso',
      type: 'GET',
      data: data
    });
  };

  /** get response rate for Merchant
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise
   */
  exports.getDataForMerchantResponseRateChart = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'response_rate_merchant',
      type: 'GET',
      data: data
    });
  };

  /** get data for Solved/unsolved ISO's dashboard widget
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise
   */
  exports.getDataForSolvedUnsolvedWidget = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'solved',
      type: 'GET',
      data: data
    });
  };

  /** get data for Big Five ISO's dashboard widget
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise
   */
  exports.getDataForBigFiveWidget = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_WIDGETS_MANAGER + 'big_five',
      type: 'GET',
      data: data
    });
  };

  /**
   * get mentions list for tracker
   *
   * @param {number} id - a tracker ID.
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise
   */
  exports.getMentionsForTracker = function(id, params) {
    var data = params || {};

    data.page = data.page || 1;

    return $.ajax({
      url: CONFIG.ISO_TRACKER_MANAGER + id + '/mentions',
      type: 'GET',
      data: data
    });
  };

  /**
   * get data for "Complaints By Source" ISO's statistics widget.
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise.
   */
  exports.getDataForComplaintsBySourceChart = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_STATISTICS + 'by_source',
      type: 'GET',
      data: data
    });
  };

  /**
   * get data for "Complaints Over Time" ISO's statistics widget.
   *
   * @param {object} params - data params for AJAX.
   * @returns {ajax} jquery ajax promise.
   */
  exports.getDataForComplaintsOverTimeChart = function(params) {
    var data = params || {};

    return $.ajax({
      url: CONFIG.ISO_STATISTICS + 'by_time',
      type: 'GET',
      data: data
    });
  };

  /**
   * init the module
   *
   * @returns {undefined}
   */
  exports.init = function() {
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        var csrfToken = Cookies.get('csrftoken');
        if (!_csrfSafeMethod(settings.type) && _sameOrigin(settings.url)) {
          // send the token to same-origin, relative URLs only.
          // send the token only if the method warrants CSRF protection
          // using the CSRFToken value acquired earlier
          xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }
      }
    });
  };

  return exports;
}($, _, Cookies, CONFIG));

AJAX.init();
