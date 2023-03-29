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
	<NcModal :show="showCheckDaemonModal"
		:title="t('api_gateway_framework', 'Check daemon connection')"
		@close="onClose">
		<div class="daemon-check-modal">
			<div class="daemon-check-modal-header">
				<h2>
					{{ t('api_gateway_framework', 'Check daemon connection') }}
				</h2>
			</div>
			<div class="input-field">
				<label for="daemon-name">
					{{ t('api_gateway_framework', 'Daemon name') }}
				</label>
				<NcInputField id="daemon-hostname"
					:value="daemonName"
					:label-outside="true"
					:disabled="true"
					:placeholder="t('api_gateway_framework', 'e.g. Default')" />
			</div>
			<NcButton
				:disabled="inputFieldsIsValid"
				:aria-label="t('api_gateway_framework', 'Update daemon connection')"
				@click="updateDaemonConnection">
				<template v-if="updatingDaemon" #icon>
					<span class="icon-loading-small" />
				</template>
				{{ t('api_gateway_framework', 'Update daemon connection') }}
			</NcButton>
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

export default {
	name: 'DaemonCheck',
	components: {
		NcButton,
		NcModal,
		NcSelect,
		NcInputField,
	},
	props: {
		showCheckDaemonModal: {
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
			daemonStatus: {},
		}
	},
	computed: {
		inputFieldsIsValid() {
			return this.daemonName === '' && this.daemonHost === '' && this.daemonPort === ''
		},
	},
	beforeMount() {
		const daemonConfig = JSON.parse(this.daemon.config)
		this.daemonProtocol = daemonConfig.protocol
		this.daemonHost = daemonConfig.host
		this.daemonPort = daemonConfig.port
		this.daemonName = this.daemon.name
		this.daemonHostType = this.daemon.type
	},
	methods: {
		onClose() {
			this.$emit('update:showCheckDaemonModal', false)
			emit('on_close_daemon_edit')
		},
		updateDaemonConnection() {
			const daemonConfig = {
				type: this.daemonHostType,
				name: this.daemonName.trim(),
				protocol: this.daemonProtocol.trim(),
				host: this.daemonHost.trim(),
				port: this.daemonPort.trim(),
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
	},
}
</script>

<style lang="scss" scoped>
.daemon-check-modal {
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
