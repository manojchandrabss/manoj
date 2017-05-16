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
