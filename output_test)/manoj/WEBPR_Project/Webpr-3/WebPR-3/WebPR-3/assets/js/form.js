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
