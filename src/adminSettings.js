/* jshint esversion: 6 */

import Vue from 'vue'
import './bootstrap.js'
import AdminSettings from './components/settings/AdminSettings.vue'

// eslint-disable-next-line
'use strict'

// eslint-disable-next-line
new Vue({
	el: '#cloud_api_gateway_prefs',
	render: h => h(AdminSettings),
})
