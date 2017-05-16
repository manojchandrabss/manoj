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
