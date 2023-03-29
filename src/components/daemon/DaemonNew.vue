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
	<NcModal :show="showNewDaemonModal"
		:title="t('api_gateway_framework', 'New daemon connection')"
		@close="onClose">
		<div class="daemon-new-modal">
			<div class="daemon-new-modal-header">
				<h2>
					{{ t('api_gateway_framework', 'New daemon connection') }}
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
			<NcButton
				:disabled="inputFieldsIsValid"
				:aria-label="t('api_gateway_framework', 'Save new daemon connection')"
				@click="postNewDaemonConnection">
				<template v-if="savingNewDaemon" #icon>
					<span class="icon-loading-small" />
				</template>
				{{ t('api_gateway_framework', 'Save new daemon connection') }}
			</NcButton>
		</div>
	</NcModal>
</template>

<script>
import axios from '@nextcloud/axios'
import { generateUrl } from '@nextcloud/router'
import { showSuccess, showError } from '@nextcloud/dialogs'

import NcSelect from '@nextcloud/vue/dist/Components/NcSelect.js'
import NcModal from '@nextcloud/vue/dist/Components/NcModal.js'
import NcInputField from '@nextcloud/vue/dist/Components/NcInputField.js'
import NcButton from '@nextcloud/vue/dist/Components/NcButton.js'

export default {
	name: 'DaemonNew',
	components: {
		NcButton,
		NcModal,
		NcSelect,
		NcInputField,
	},
	props: {
		showNewDaemonModal: {
			type: Boolean,
			required: true,
			default: false,
		},
		daemons: {
			type: Array,
			required: true,
			default: () => [],
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
			savingNewDaemon: false,
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
	watch: {
		daemonHostType(newDaemonHostType) {
			if (newDaemonHostType === 'local') {
				// Set default values for local type
				this.daemonProtocol = 'http'
				this.daemonHost = 'localhost'
				this.daemonPort = '8063'
				this.daemonXAuth = 'nextcloud:'
			} else if (newDaemonHostType === 'remote') {
				// Set default values for remote type
				this.daemonProtocol = 'https'
				this.daemonHost = ''
				this.daemonPort = '8463'
				this.daemonXAuth = ''
			}
		},
	},
	methods: {
		onClose() {
			this.$emit('update:showNewDaemonModal', false)
			this.setFormDefaults()
		},
		postNewDaemonConnection() {
			const daemonConfig = {
				type: this.daemonHostType,
				name: this.daemonName.trim(),
				protocol: this.daemonProtocol.trim(),
				host: this.daemonHost.trim(),
				port: this.daemonPort.trim(),
				xAuth: this.daemonXAuth.trim(),
			}
			this.savingNewDaemon = true
			axios.post(generateUrl('/apps/api_gateway_framework/daemon'), { daemonConfig })
				.then(res => {
					console.debug(res)
					if (res.status === 200) {
						this.savingNewDaemon = false
						const newDaemons = [...this.daemons, res.data.daemon]
						this.$emit('update:daemons', newDaemons)
						showSuccess(t('api_gateway_framework', 'New daemon connection saved'))
						this.onClose()
					}
				})
				.catch(error => {
					console.debug(error)
					this.savingNewDaemon = false
					if (error.response.status === 409) {
						showError(t('api_gateway_framework', 'Daemon connection with this name already exists'))
						return
					}
					showError(t('api_gateway_framework', 'Error while saving new daemon connection'))
				})
		},
		setFormDefaults() {
			if (this.daemonHostType === 'local') {
				// Set default values for local type
				this.daemonProtocol = 'http'
				this.daemonHost = 'localhost'
				this.daemonPort = '8063'
				this.daemonXAuth = 'nextcloud:'
			} else if (this.daemonHostType === 'remote') {
				// Set default values for remote type
				this.daemonProtocol = 'https'
				this.daemonHost = ''
				this.daemonPort = '8463'
				this.daemonXAuth = ''
			}
		},
	},
}
</script>

<style lang="scss" scoped>
.daemon-new-modal {
	padding: 50px;
}

.input-field {
	margin-bottom: 20px;

	label {
		margin-bottom: 5px;
		margin-right: 5px;
	}
}
</style>
