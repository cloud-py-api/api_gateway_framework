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
	<NcModal :show="showEditDaemonModal"
		:title="t('api_gateway_framework', 'Edit daemon connection')"
		@close="onClose">
		<div class="daemon-edit-modal">
			<div class="daemon-edit-modal-header">
				<h2>
					{{ t('api_gateway_framework', 'Edit daemon connection') }}
				</h2>
			</div>
			<div class="input-field">
				<label for="daemon-name">
					{{ t('api_gateway_framework', 'Daemon name') }}
				</label>
				<NcInputField id="daemon-hostname"
					:value.sync="daemonName"
					:label-outside="true"
					:placeholder="t('api_gateway_framework', 'e.g. Default')" />
			</div>
			<div class="input-field">
				<label for="daemon-host-type">
					{{ t('api_gateway_framework', 'Daemon host type') }}
				</label>
				<NcSelect v-model="daemonHostType"
					input-id="daemon-host-type"
					:clearable="false"
					:options="daemonHostTypes"
					:label-outside="true" />
			</div>
			<div class="input-field">
				<label for="daemon-host-protocol">
					{{ t('api_gateway_framework', 'Daemon host protocol') }}
				</label>
				<NcSelect v-model="daemonProtocol"
					input-id="daemon-host-protocol"
					:clearable="false"
					:options="daemonProtocols"
					:label-outside="true" />
			</div>
			<div class="input-field">
				<label for="daemon-host">
					{{ t('api_gateway_framework', 'Daemon host') }}
				</label>
				<NcInputField id="daemon-host"
					:value.sync="daemonHost"
					:label-outside="true"
					:placeholder="t('api_gateway_framework', 'e.g. localhost')" />
			</div>
			<div class="input-field">
				<label for="daemon-port">
					{{ t('api_gateway_framework', 'Daemon port') }}
				</label>
				<NcInputField id="daemon-port"
					:value.sync="daemonPort"
					:label-outside="true"
					:placeholder="t('api_gateway_framework', 'e.g. 8063')" />
			</div>
			<div class="input-field">
				<label for="daemon-x-auth">
					{{ t('api_gateway_framework', 'Daemon xAuth') }}
				</label>
				<!-- TODO: Add validation of xAuth for base64 encoding -->
				<NcInputField id="daemon-x-auth"
					:value.sync="daemonXAuth"
					:label-outside="true"
					:placeholder="t('api_gateway_framework', 'e.g. nextcloud:password')" />
			</div>
			<div class="actions">
				<NcButton type="primary"
					:disabled="inputFieldsIsValid"
					:aria-label="t('api_gateway_framework', 'Update daemon connection')"
					@click="updateDaemonConnection">
					<template v-if="updatingDaemon" #icon>
						<span class="icon-loading-small" />
					</template>
					{{ t('api_gateway_framework', 'Update daemon connection') }}
				</NcButton>
				<NcButton :aria-label="t('api_gateway_framework', 'Verify daemon connection')"
					@click="checkConnectionToDaemon(daemon)">
					<template #icon>
						<AlertCircleOutline v-if="daemonError" :size="18" />
						<CloudCheckVariantOutline v-else-if="!checkingConnection" :size="18" />
						<span v-else class="material-design-icon icon-loading-small" />
					</template>
					{{ t('api_gateway_framework', 'Check connection') }}
				</NcButton>
			</div>
		</div>
	</NcModal>
</template>

<script>
import axios from '@nextcloud/axios'
import { generateUrl } from '@nextcloud/router'
import { showSuccess, showError } from '@nextcloud/dialogs'
import { emit } from '@nextcloud/event-bus'

import NcSelect from '@nextcloud/vue/dist/Components/NcSelect.js'
import NcModal from '@nextcloud/vue/dist/Components/NcModal.js'
import NcInputField from '@nextcloud/vue/dist/Components/NcInputField.js'
import NcButton from '@nextcloud/vue/dist/Components/NcButton.js'

import CloudCheckVariantOutline from 'vue-material-design-icons/CloudCheckVariantOutline.vue'
import AlertCircleOutline from 'vue-material-design-icons/AlertCircleOutline.vue'

export default {
	name: 'DaemonEdit',
	components: {
		NcButton,
		NcModal,
		NcSelect,
		NcInputField,
		CloudCheckVariantOutline,
		AlertCircleOutline,
	},
	props: {
		showEditDaemonModal: {
			type: Boolean,
			required: true,
			default: false,
		},
		daemons: {
			type: Array,
			required: true,
			default: () => [],
		},
		daemon: {
			type: Object,
			required: true,
			default: () => {},
		},
	},
	data() {
		return {
			daemonHostType: 'local',
			daemonHostTypes: [
				'local',
				'remote',
			],
			daemonProtocol: 'http',
			daemonProtocols: [
				'http',
				'https',
			],
			daemonName: '',
			daemonHost: 'localhost',
			daemonPort: '8063',
			daemonXAuth: 'nextcloud:',
			updatingDaemon: false,
			checkingConnection: false,
			daemonError: false,
		}
	},
	computed: {
		inputFieldsIsValid() {
			return this.daemonName === ''
				|| this.daemonHost === ''
				|| this.daemonPort === ''
				|| this.daemonXAuth === ''
		},
	},
	beforeMount() {
		const daemonConfig = JSON.parse(this.daemon.config)
		this.daemonName = this.daemon.name
		this.daemonHostType = this.daemon.type
		this.daemonProtocol = daemonConfig.protocol
		this.daemonHost = daemonConfig.host
		this.daemonPort = daemonConfig.port
		this.daemonXAuth = daemonConfig.xAuth
	},
	methods: {
		onClose() {
			this.$emit('update:showEditDaemonModal', false)
			emit('on_close_daemon_edit')
		},
		updateDaemonConnection() {
			const daemonConfig = {
				type: this.daemonHostType,
				name: this.daemonName.trim(),
				protocol: this.daemonProtocol.trim(),
				host: this.daemonHost.trim(),
				port: this.daemonPort.trim(),
				xAuth: this.daemonXAuth.trim(),
			}
			this.updatingDaemon = true
			axios.put(generateUrl(`/apps/api_gateway_framework/daemon/${this.daemon.id}`), { daemonConfig })
				.then(res => {
					console.debug(res)
					if (res.status === 200) {
						emit('update_daemon', res.data.daemon)
						showSuccess(t('api_gateway_framework', 'New daemon connection updated'))
						this.onClose()
					}
					this.updatingDaemon = false
				})
				.catch(error => {
					console.debug(error)
					this.updatingDaemon = false
					showError(t('api_gateway_framework', 'Error while updating daemon connection'))
				})
		},
		checkConnectionToDaemon(daemon) {
			this.checkingConnection = true
			this.daemonError = false
			const daemonConfig = {
				type: this.daemonHostType,
				name: this.daemonName.trim(),
				protocol: this.daemonProtocol.trim(),
				host: this.daemonHost.trim(),
				port: this.daemonPort.trim(),
				xAuth: this.daemonXAuth.trim(),
			}
			axios.post(generateUrl(`/apps/api_gateway_framework/daemon/${daemon.id}/config-check`), {
				daemonConfig,
			})
				.then(res => {
					this.checkingConnection = false
					emit('set-daemon-check-status', res.data)
					if (res.status === 200) {
						showSuccess(t('api_gateway_framework', 'Connection to daemon is successful'))
					} else {
						showError(t('api_gateway_framework', 'Connection to daemon is failed'))
					}
				})
				.catch((error) => {
					console.debug(error)
					this.checkingConnection = false
					this.daemonError = true
					showError(t('api_gateway_framework', 'Error while checking connection to daemon'))
				})
		},
	},
}
</script>

<style lang="scss" scoped>
.daemon-edit-modal {
	padding: 50px;

	.actions {
		display: flex;

		& > button:first-child {
			margin-right: 10px;
		}
	}
}

.input-field {
	margin-bottom: 20px;

	label {
		margin-bottom: 5px;
		margin-right: 5px;
	}
}
</style>
