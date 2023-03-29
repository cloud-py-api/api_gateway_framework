<!--
 - @copyright Copyright (c) 2023 Andrey Borysenko <andrey18106x@gmail.com>
 -
 - @copyright Copyright (c) 2023 Alexander Piskun <bigcat88@icloud.com>
 -
 - @author 2023 Andrey Borysenko <andrey18106x@gmail.com>
 -
 - @license AGPL-3.0-or-later
 -
 - This program is free software: you can redistribute it and/or modify
 - it under the terms of the GNU Affero General Public License as
 - published by the Free Software Foundation, either version 3 of the
 - License, or (at your option) any later version.
 -
 - This program is distributed in the hope that it will be useful,
 - but WITHOUT ANY WARRANTY; without even the implied warranty of
 - MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 - GNU Affero General Public License for more details.
 -
 - You should have received a copy of the GNU Affero General Public License
 - along with this program. If not, see <http://www.gnu.org/licenses/>.
 -
 -->

<template>
	<div id="cloud_api_gateway_framework_prefs" class="section">
		<div class="section-heading">
			<h2>
				{{ t('api_gateway_framework', 'Nextcloud API Gateway Framework') }}
			</h2>
			<p>
				{{ t('api_gateway_framework', 'Nextcloud API Gateway Framework is a framework for creating API gateways for Nextcloud. It allows Nextcloud apps to have an external part for heavy computings, so the Nextcloud instance performance is not affected') }}
			</p>
		</div>
		<NcSettingsSection :title="t('api_gateway_framework', 'Daemons')"
			:description="t('api_gateway_framework', 'External apps daemons configuration')">
			<div v-if="daemons.length > 0" class="actions">
				<NcButton :label="t('api_gateway_framework', 'Configure new daemon connection')"
					type="primary"
					style="margin-right: 10px;"
					@click="showNewDaemonModal">
					<template #icon>
						<Plus :size="20" />
					</template>
					{{ t('api_gateway_framework', 'Add new daemon connection') }}
				</NcButton>
				<NcButton :label="t('api_gateway_framework', 'Check connection to all daemons')"
					type="secondary"
					:disabled="false"
					@click="checkConnectionToDaemons">
					<template v-if="daemonsCheck" #icon>
						<span class="icon-loading-small" />
					</template>
					{{ t('api_gateway_framework', 'Check connection to daemons') }}
				</NcButton>
			</div>
			<!-- List daemons -->
			<div class="daemons">
				<div v-if="daemons.length > 0" class="daemons-list">
					<DaemonItem v-for="daemon in daemons"
						:key="daemon.id"
						:daemon="daemon"
						:daemons.sync="daemons" />
				</div>
				<!-- Empty content -->
				<NcEmptyContent v-else
					:title="t('api_gateway_framework', 'No daemons configured')"
					style="margin-top: 20px;">
					<template #icon>
						<FormatListText :size="20" />
					</template>
					<template #action>
						<NcButton
							:label="t('api_gateway_framework', 'Configure new daemon connection')"
							type="primary"
							:disabled="false"
							@click="showNewDaemonModal">
							{{ t('api_gateway_framework', 'Configure new daemon connection') }}
						</NcButton>
					</template>
				</NcEmptyContent>
			</div>
		</NcSettingsSection>
		<DaemonNew v-if="configureNewDaemon"
			:show-new-daemon-modal.sync="configureNewDaemon"
			:daemons.sync="daemons" />
		<DaemonEdit v-if="showEditDaemonModal"
			:show-edit-daemon-modal.sync="showEditDaemonModal"
			:daemon="daemonToEdit"
			:daemons.sync="daemons" />
		<NcSettingsSection :title="t('api_gateway_framework', 'Testing')"
			:description="t('api_gateway_framework', 'External apps daemons tests')">
			<div class="test-app-run" style="display: flex; flex-direction: column; width: fit-content;">
				<NcSelect v-if="daemons.length > 0"
					v-model="testDaemon"
					input-id="test_daemon"
					:options="testDaemonsList"
					:placeholder="t('api_gateway_framework', 'Select target daemon')"
					style="margin-bottom: 20px;" />
				<div class="input-field">
					<label for="test-app-name" style="margin-right: 10px;">
						{{ t('api_gateway_framework', 'Test app name:') }}
					</label>
					<NcInputField id="test-app-name"
						:value.sync="testAppName"
						:label-outside="true"
						:placeholder="t('api_gateway_framework', 'e.g. hello_world')"
						style="margin-bottom: 20px;" />
				</div>
				<NcButton v-if="daemons.length > 0"
					:label="t('api_gateway_framework', 'Run test app')"
					type="secondary"
					@click="runTestApp">
					<template v-if="runningTestApp" #icon>
						<span class="icon-loading-small" />
					</template>
					{{ t('api_gateway_framework', 'Run test app') }}
				</NcButton>
			</div>
		</NcSettingsSection>
		<!-- TODO: Add bug report section with retrieving information from configured daemons -->
	</div>
</template>

<script>
import axios from '@nextcloud/axios'
import { showSuccess, showError } from '@nextcloud/dialogs'
import { generateUrl } from '@nextcloud/router'
import { loadState } from '@nextcloud/initial-state'
import { subscribe, unsubscribe, emit } from '@nextcloud/event-bus'

import NcSettingsSection from '@nextcloud/vue/dist/Components/NcSettingsSection.js'
import NcButton from '@nextcloud/vue/dist/Components/NcButton.js'
import NcSelect from '@nextcloud/vue/dist/Components/NcSelect.js'
import NcInputField from '@nextcloud/vue/dist/Components/NcInputField.js'
import NcEmptyContent from '@nextcloud/vue/dist/Components/NcEmptyContent.js'
import FormatListText from 'vue-material-design-icons/FormatListText.vue'
import Plus from 'vue-material-design-icons/Plus.vue'

import DaemonItem from '../daemon/DaemonItem.vue'
import DaemonEdit from '../daemon/DaemonEdit.vue'
import DaemonNew from '../daemon/DaemonNew.vue'

export default {
	name: 'AdminSettings',
	components: {
		NcSettingsSection,
		NcButton,
		NcSelect,
		NcEmptyContent,
		NcInputField,
		FormatListText,
		DaemonItem,
		DaemonNew,
		DaemonEdit,
		Plus,
	},
	data() {
		return {
			daemonsCheck: false,
			daemonsCheckError: false,
			configureNewDaemon: false,
			xAuthToken: '',
			daemons: loadState('api_gateway_framework', 'daemons'),
			showEditDaemonModal: false,
			daemonToEdit: {},
			testAppName: 'hello_world',
			testDaemon: null,
			runningTestApp: false,
		}
	},
	computed: {
		testDaemonsList() {
			return this.daemons.map((d) => {
				return {
					id: d.id,
					label: d.name,
				}
			})
		},
	},
	beforeMount() {
		subscribe('edit_daemon', (daemon) => {
			this.showEditDaemonModal = true
			this.daemonToEdit = daemon
		})
		subscribe('update_daemon', (daemon) => {
			this.daemons = this.daemons.map((d) => {
				if (d.id === daemon.id) {
					return daemon
				}
				return d
			})
		})
		subscribe('on_close_daemon_edit', () => {
			this.showEditDaemonModal = false
			this.daemonToEdit = {}
		})
	},
	beforeDestroy() {
		unsubscribe('edit_daemon')
		unsubscribe('update_daemon')
		unsubscribe('on_close_daemon_edit')
	},
	methods: {
		checkConnectionToDaemons() {
			this.daemonsCheck = true
			axios.post(generateUrl('/apps/api_gateway_framework/daemons-check'))
				.then((response) => {
					console.debug(response)
					this.daemonsCheck = false
					if (response.status === 200) {
						response.data.forEach(daemonStatus => {
							emit('set-daemon-check-status', daemonStatus)
						})
						if (response.data.every(daemonStatus => daemonStatus.status === 200)) {
							showSuccess(t('api_gateway_framework', 'Connection to all daemons is successful'))
						} else {
							showError(t('api_gateway_framework', 'Connection to some daemons is not successful'))
						}
					}
				})
				.catch((error) => {
					console.debug(error)
					this.daemonsCheck = false
					this.daemonsCheckError = true
					showError(t('api_gateway_framework', 'Error while checking connection to all daemons'))
				})
		},
		showNewDaemonModal() {
			this.configureNewDaemon = true
		},
		runTestApp() {
			if (this.testDaemon === null) {
				showError(t('api_gateway_framework', 'Please select target daemon'))
				return
			}
			this.runningTestApp = true
			axios.post(generateUrl('/apps/api_gateway_framework/daemon/run'), {
				app: this.testAppName,
				daemonId: this.testDaemon.id,
			})
				.then((response) => {
					console.debug(response)
					if (response.status === 200) {
						showSuccess(t('api_gateway_framework', 'Test app executed successfully'))
					}
					this.runningTestApp = false
				})
				.catch((error) => {
					console.debug(error)
					this.runningTestApp = false
					showError(t('api_gateway_framework', 'Error while executing test app'))
				})
		},
	},
}
</script>

<style lang="scss" scoped>
.section-heading {
	margin: 0 30px;
}

.daemons-list {
	margin: 20px 0;
	width: 100%;
	max-width: 540px;
	max-height: 320px;
	overflow-y: auto;
}

.actions {
	display: flex;
}
</style>
