/* exported CONFIG */
'use strict';

/**
 *  configuration variables for application
 *
 *  @namespace
 */
var CONFIG = {

  /**
   * base path
   */
  BASE: '/',

  /**
   * path for api endpoints related to manage merchants
   */
  get MERCHANT_MANAGER() {
    return this.BASE + String('merchant/');
  },

  /**
   * path for api endpoints related to manage todos
   */
  get TODO_MANAGER() {
    return this.BASE + String('todo/');
  },

  /**
   * path for api endpoints related to manage users
   */
  get USER_MANAGER() {
    return this.BASE + String('users/');
  },

  /**
   * path for ISO manager
   */
  get ISO_MANAGER() {
    return this.BASE;
  },

  /**
   * path for ISO's widgets manager
   */
  get ISO_WIDGETS_MANAGER() {
    return this.ISO_MANAGER;
  },

  /**
   * path for tracker manager
   */
  get ISO_TRACKER_MANAGER() {
    return this.ISO_MANAGER + String('tracker/');
  },

  /**
   * path for ISO's statistics
   */
  get ISO_STATISTICS() {
    return this.ISO_MANAGER + String('statistics/');
  },

  /**
   * charts
   */
  MAX_LABEL_LENGTH: 30
};

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

/* globals $, _, Chart */
/* exported CHARTS */
'use strict';

/**
 * perfomance tracking for widget on the ISO dashboard.
 *
 * @version 1.0
 */
var CHARTS = (function($, _, Chart) {
  // define exportable methods of the module
  var exports = {},
    charts = {};

  /**
   * perfomance tracking widget.
   *
   * @param {object} scores Datasets for .
   * @param {string} xLegend A param for Chart.
   * @returns {undefined}
   */
  exports.buildPerformanceTrackerChart = function(scores, xLegend) {
    var ctx = $('#tracking'),
      data = {
        labels: xLegend,
        datasets: []
      },
      options = {
        elements: {
          point: {
            radius: 3
          }
        },
        legend: {
          position: 'bottom',
          fullWidth: true,
          labels: {
            boxWidth: 12,
            padding: 5
          }
        },
        scales: {
          xAxes: [{
            gridLines: {
              display: false
            }
          }]
        }
      };

    _.each(scores, function(score) {
      data.datasets.push({
        label: TOOLS.truncatechars(score.label, CONFIG.MAX_LABEL_LENGTH),
        data: score.data,
        borderColor: score.color,
        borderWidth: 2,
        backgroundColor: score.color,
        tension: 0,
        fill: false
      });
    });

    if ('chartTracking' in charts) {
      charts.chartTracking.destroy();
    }
    charts.chartTracking = new Chart(ctx, {
      type: 'line',
      data: data,
      options: options
    });
  };

  /**
   * mention chart.
   *
   * @param {list} negative A param for Chart.
   * @param {list} positive A param for Chart.
   * @param {list} neutral A param for Chart.
   * @param {list} legend - data for a legend of the chart.
   * @returns {undefined}
   */
  exports.buildMentionsChart = function(negative, positive, neutral,
                                        legend) {
    var ctx = $('#mentions'),
      data = {
        labels: legend,

        datasets: [
          {
            label: 'Pos',
            borderColor: '#0fb474',
            pointColor: '#0fb474',
            data: positive,
            borderWidth: 2,
            backgroundColor: '#0fb474',
            tension: 0,
            fill: false
          },
          {
            label: 'Neg',
            borderColor: '#d0021b',
            pointColor: '#d0021b',
            data: negative,
            borderWidth: 2,
            backgroundColor: '#d0021b',
            tension: 0,
            fill: false
          },
          {
            label: 'Neutral',
            borderColor: '#d1ddea',
            pointColor: '#d1ddea',
            data: neutral,
            borderWidth: 2,
            backgroundColor: '#d1ddea',
            tension: 0,
            fill: false
          }
        ]
      },
      options = {
        elements: {
          point: {
            radius: 3
          }
        },
        legend: {
          position: 'bottom',
          fullWidth: true,
          labels: {
            boxWidth: 12,
            padding: 5
          }
        },
        scales: {
          xAxes: [{
            gridLines: {
              display: false
            }
          }]
        }
      };

    if ('mentionsChart' in charts) {
      charts.mentionsChart.destroy();
    }
    charts.mentionsChart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: options
    });
  };

  /**
   * mention chart.
   *
   * @param {string} negative A param for Chart.
   * @param {string} positive A param for Chart.
   * @param {string} neutral A param for Chart.
   * @returns {undefined}
   */
  exports.buildMerchantMentionsChart = function(negative, positive, neutral) {
    var ctx = $('#mentions'),
      LABELS_COUNT = 7,
      data = {
        labels: Array(LABELS_COUNT),
        datasets: [{
          label: 'Pos',
          borderColor: '#0fb474',
          pointColor: '#0fb474',
          data: positive,
          tension: 0,
          borderWidth: 2,
          backgroundColor: '#0fb474',
          fill: false
        }, {
          label: 'Neg',
          borderColor: '#d0021b',
          pointColor: '#d0021b',
          data: negative,
          tension: 0,
          borderWidth: 2,
          backgroundColor: '#d0021b',
          fill: false
        }, {
          label: 'Neutral',
          borderColor: '#d1ddea',
          pointColor: '#d1ddea',
          data: neutral,
          tension: 0,
          borderWidth: 2,
          backgroundColor: '#d1ddea',
          fill: false
        }]
      },
      options = {
        scales: {
          xAxes: [{
            display: false
          }],
          yAxes: [{
            display: false
          }]
        },
        legend: {
          position: 'top',
          fullWidth: true,
          labels: {
            boxWidth: 12,
            padding: 5
          }
        }
      };

    if ('merchantMentionsChart' in charts) {
      charts.merchantMentionsChart.destroy();
    }
    charts.merchantMentionsChart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: options
    });
  };

  /**
   * build response rate chart.
   *
   * @param {object} container - a jQuery object that contains canvas.
   * @param {number} solved - a param for Chart.
   * @param {number} unsolved - a param for Chart.
   * @returns {undefined}
   */
  exports.buildResponseRateChart = function(container, solved, unsolved) {
    var ctx = container.find('canvas'),
      data = {
        labels: ['solved', 'unsolved'],
        datasets: [
          {
            data: [
              solved,
              unsolved
            ],
            backgroundColor: [
              '#0fb474',
              '#d0021b'
            ]
          }]
      },
      options = {
        cutoutPercentage: 80,
        legend: {
          display: false
        },
        tooltips: {
          enabled: false
        }
      };

    if ('responseRate' in charts) {
      charts.responseRate.destroy();
    }
    charts.responseRate = new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: options,
      animation: {
        animateScale: true
      }
    });
  };

  /**
   * build the Pie chart with data from server.
   *
   * @param {object} container - an object that contains canvas for the chart.
   * @param {list} labels - labels list for the chart.
   * @param {object} datasets - data for the chart.
   * @return {undefined}
   */
  exports.buildIndustriesComplaintsChart = function(container, labels,
                                                    datasets) {
    var ctx = container.find('canvas'),
      labelTemplate = _.template('Neg.: { neg } ({ perc }%)'),
      noDataMessage = container.find('.no-data-message');

    // show or hide message if there is data
    noDataMessage[(labels.length ? 'add' : 'remove') + 'Class']('hidden');
    // destroy chart if exists
    if ('industriesComplaints' in charts) {
      charts.industriesComplaints.destroy();
    }
    // build chart and set responsed data
    charts.industriesComplaints = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: datasets.data,
          backgroundColor: datasets.backgroundColor
        }]
      },
      options: {
        cutoutPercentage: 30,
        legend: {
          display: false
        },
        tooltips: {
          // extends tooltip`s content
          callbacks: {
            // an industry name
            title: function(tooltip) {
              return TOOLS.truncatechars(labels[tooltip[0].index],
                                         CONFIG.MAX_LABEL_LENGTH);
            },
            label: function(tooltip) {
              return labelTemplate({
                neg: datasets.data[tooltip.index],
                perc: Math.round(datasets.extData[tooltip.index])
              });
            }
          }
        }
      }
    });
  };

  /**
   * function for rendering sparklines charts
   *
   * @param {object} container - an object that contains canvas for the chart.
   * @param {array} data - data for the chart.
   * @returns {undefined}
   */
  exports.buildSparklineChart = function(container, data) {
    var ctx = container.find('canvas'),
      options = {
        legend: {
          display: false
        },
        tooltips: {
          enabled: false
        },
        elements: {
          point: {
            radius: 0
          }
        },
        scales: {
          lineTension: 0,
          xAxes: [{
            display: false
          }],
          yAxes: [{
            display: false
          }]
        }
      };

    charts.sparklineCharts = charts.sparklineCharts || [];

    charts.sparklineCharts.push(new Chart(ctx, {
      type: 'line',
      data: {
        labels: Array(data.length),
        datasets: [{
          data: data
        }]
      },
      options: options
    }));
  };

  /**
   * function for rendering "Complaints by source" chart.
   *
   * @param {object} container - an object that contains canvas for the chart.
   * @param {array} id - id of chart, default 0.
   * @param {array} data - array of data arrays for the chart.
   * @returns {undefined}
   */
  exports.buildComplaintsBySourceChart = function(container, id, data) {
    var ctx = container.find('canvas'),
      chartId = id || 0;

    if ('complaintsBySourceChart' + chartId in charts) {
      charts['complaintsBySourceChart' + chartId].destroy();
    }

    charts['complaintsBySourceChart' + chartId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Merchant/Industry',
            backgroundColor: 'rgba(26, 115, 105, 1)',
            borderColor: 'rgba(26, 115, 105, 1)',
            borderWidth: 1,
            hoverBackgroundColor: 'rgba(26, 115, 105, .8)',
            hoverBorderColor: 'rgba(26, 115, 105, .8)',
            data: data.merchant
          }, {
            label: 'Average',
            backgroundColor: 'rgba(121, 229, 210, 1)',
            borderColor: 'rgba(121, 229, 210, 1)',
            borderWidth: 1,
            hoverBackgroundColor: 'rgba(121, 229, 210, .8)',
            hoverBorderColor: 'rgba(121, 229, 210, .8)',
            data: data.average
          }
        ]
      },
      options: {
        legend: {
          display: false
        }
      }
    });
  };

  /**
   * function for rendering "Complaints Over Time" chart.
   *
   * @param {object} container - an object that contains canvas for the chart.
   * @param {array} id - id of chart, default 0.
   * @param {array} data - array for the chart.
   * @returns {undefined}
   */
  exports.buildComplaintsOverTimeChart = function(container, id, data) {
    var ctx = container.find('canvas'),
      chartId = id || 0,
      datasets = [];

    if ('complaintsOverTimeChart' + chartId in charts) {
      charts['complaintsOverTimeChart' + chartId].destroy();
    }

    _.each(data.datasets, function(item) {
      datasets.push({
        label: item.label,
        data: item.data,
        borderColor: item.color,
        backgroundColor: item.color,
        fill: false,
        lineTension: 0,
        borderWidth: 2
      });
    });

    charts['complaintsOverTimeChart' + chartId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.legend,
        datasets: datasets
      },
      options: {
        elements: {
          point: {
            radius: 3
          }
        },
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 5
          }
        },
        scales: {
          xAxes: [{
            gridLines: {
              display: false
            }
          }]
        }
      }
    });
  };

  exports.getCharts = function() {
    return charts;
  };

  return exports;
}($, _, Chart));

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

/* globals $, _ */
/* exported FORM */
'use strict';

/**
 * tools for works with form.
 *
 * @version 1.0
 * @param {object} form - jQuery object of the
 * @returns {undefined}
 */
var FORM = (function($, _) {
  // define exportable methods of the module
  var exports = {};

  exports.errorTemplate = _.template('<span class="help-block error">' +
                                     '<strong>{ text }</strong></span>');

  /**
   * clear exist errors
   *
   * @param {object} form - jQuery object of the form.
   * @returns {undefined}
   */
  exports.clearErrors = function(form) {
    form.find('.has-error').removeClass('has-error');
    form.find('.error').remove();
  };

  /**
   * clear exist errors
   *
   * @param {object} form - jQuery object of the form.
   * @returns {undefined}
   */
  exports.clearForm = function(form) {
    // clear fields
    form.clearForm();
    // clear errors
    exports.clearErrors(form);
  };

  /**
   * insert form errors that there are in response
   *
   * @param {object} form - jQuery object of the form.
   * @param {object} data - a responsed JSON with form errors
   * @returns {undefined}
   */
  exports.insertErrors = function(form, data) {
    // clear old errors
    exports.clearErrors(form);
    // inserting new errors
    $.each($.parseJSON(data.responseText), function(k, v) {
      form.find('#div_id_' + k).append(exports.errorTemplate({text: v}))
                               .addClass('has-error');
    });
  };

  /**
   * get search settings JSON.
   *
   * @param {object} form - a jQuery`s object of form.
   * @return {object} settings - JSON-serialized search settings.
   */
  exports.getSearchSettings = function(form) {
    var defaultSettings = {
        'official_name': [false],
        'short_name': [false, false, false],
        'product': [false, false, false]
      },
      searchSettingsStr = form.find('#id_search_settings').val() || 'null',
      settings = JSON.parse(searchSettingsStr),
      settingsExists = Boolean(settings && !(settings === 'null'));

    return settingsExists ? settings : defaultSettings;
  };

  /**
   * make JSON for search settings
   *
   * @param {form} form - a jQuery`s object of form.
   * @param {array} fields - list of fields these need to store settings.
   * @return {undefined}
   */
  exports.collectSearchSettings = function(form, fields) {
    var result = {},
      elements = [],
      targetId = null,
      checked = false,
      searchSettingsField = form.find('#id_search_settings'),
      searchFields = fields || exports.getSearchSettings(form);

    _.each(searchFields, function(settingsList, group) {
      result[group] = [];
      elements = $('#div_id_' + group).find('.form-control');

      _.each(elements, function(value) {
        targetId = $(value).attr('id');

        if ($('#' + targetId).val().trim()) {
          checked = $('[data-target=' + targetId + ']').is(':checked');
          result[group].push(checked);
        }
      });
    });

    searchSettingsField.val(JSON.stringify(result));
  };

  /**
   * add checkboxes to search fields
   *
   * @param {object} form - a jQuery`s object of form.
   * @return {undefined}
   */
  exports.addCheckboxes = function(form) {
    var checkboxHTML = null,
      checked = '',
      fields = exports.getSearchSettings(form),
      elements = null,
      targetId = null;

    _.each(fields, function(value, group) {
      elements = $('#div_id_' + group).find('.form-control');

      _.each(elements, function(value, key) {
        checked = fields[group][key] ? 'checked="checked"' : '';
        targetId = $(value).attr('id');
        checkboxHTML = String(
          '<div class="checkbox checkbox-custom">' +
            '<label>' +
              '<input ' + checked +
                      'type="checkbox" ' +
                      'data-target="' + targetId + '"/> strict search' +
            '</label>' +
          '</div>'
        );

        $(checkboxHTML).insertAfter('#' + targetId);
      });
    });
  };

  return exports;
}($, _));

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
