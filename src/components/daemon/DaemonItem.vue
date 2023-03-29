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
	<NcListItem
		:title="daemon.name"
		:bold="true"
		:details="daemonDetailsIfError"
		:force-display-actions="true"
		:compact="true">
		<template #icon>
			<Connection :size="20" />
		</template>
		<template #subtitle>
			{{ daemonSubtitle }}
		</template>
		<template #actions>
			<NcActionButton :aria-label="t('api_gateway_framework', 'Verify daemon connection')"
				@click="checkConnectionToDaemon(daemon)">
				<template #icon>
					<AlertCircleOutline v-if="daemonError" :size="18" />
					<CloudCheckVariantOutline v-else-if="!checkingConnection" :size="18" />
					<span v-else class="material-design-icon icon-loading-small" />
				</template>
				{{ t('api_gateway_framework', 'Check connection') }}
			</NcActionButton>
			<NcActionButton :aria-label="t('api_gateway_framework', 'Edit daemon connection')"
				:close-after-click="true"
				@click="showDaemonModal(daemon)">
				<template #icon>
					<span class="material-design-icon icon-rename" />
				</template>
				{{ t('api_gateway_framework', 'Edit daemon') }}
			</NcActionButton>
			<NcActionButton :aria-label="t('api_gateway_framework', 'Delete daemon connection')"
				@click="deleteDaemon(daemon)">
				<template #icon>
					<span v-if="!deletingDaemon" class="material-design-icon icon-delete" />
					<span v-else class="material-design-icon icon-loading-small" />
				</template>
				{{ t('api_gateway_framework', 'Delete') }}
			</NcActionButton>
		</template>
	</NcListItem>
</template>

<script>
import axios from '@nextcloud/axios'
import { showSuccess, showError } from '@nextcloud/dialogs'
import { generateUrl } from '@nextcloud/router'
import { subscribe, unsubscribe, emit } from '@nextcloud/event-bus'

import NcActionButton from '@nextcloud/vue/dist/Components/NcActionButton.js'
import NcListItem from '@nextcloud/vue/dist/Components/NcListItem.js'

import CloudCheckVariantOutline from 'vue-material-design-icons/CloudCheckVariantOutline.vue'
import AlertCircleOutline from 'vue-material-design-icons/AlertCircleOutline.vue'
import Connection from 'vue-material-design-icons/Connection.vue'

export default {
	name: 'DaemonItem',
	components: {
		NcListItem,
		NcActionButton,
		CloudCheckVariantOutline,
		Connection,
		AlertCircleOutline,
	},
	props: {
		daemon: {
			type: Object,
			required: true,
		},
		daemons: {
			type: Array,
			required: true,
		},
	},
	data() {
		return {
			daemonError: false,
			checkingConnection: false,
			deletingDaemon: false,
		}
	},
	computed: {
		daemonSubtitle() {
			if (this.daemon.config != null) {
				const config = JSON.parse(this.daemon.config)
				return `${this.daemon.type} - ${config.host}:${config.port}`
			}
			return this.daemon.type
		},
		daemonDetailsIfError() {
			if (this.daemonError) {
				return t('api_gateway_framework', 'Error while checking connection to daemon')
			}
			return ''
		},
	},
	beforeMount() {
		subscribe('set-daemon-check-status', (daemonStatus) => {
			if (daemonStatus.daemon.id === this.daemon.id) {
				console.debug('set-daemon-check-status: ', daemonStatus)
				console.debug('set-daemon-check-status: ', !(daemonStatus.status === 200))
				this.daemonError = !(daemonStatus.status === 200)
			}
		})
	},
	beforeDestroy() {
		unsubscribe('set-daemon-check-status')
	},
	methods: {
		checkConnectionToDaemon(daemon) {
			this.checkingConnection = true
			this.daemonError = false
			axios.get(generateUrl(`/apps/api_gateway_framework/daemon/${daemon.id}/status`))
				.then(res => {
					this.checkingConnection = false
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
		deleteDaemon(daemon) {
			this.deletingDaemon = true
			axios.delete(generateUrl(`/apps/api_gateway_framework/daemon/${daemon.id}`))
				.then(res => {
					this.deletingDaemon = false
					if (res.status === 200) {
						showSuccess(t('api_gateway_framework', 'Daemon connection deleted'))
						const newDaemons = this.daemons.filter(d => d.id !== daemon.id)
						this.$emit('update:daemons', newDaemons)
					}
				})
				.catch(err => {
					console.debug(err)
					this.deletingDaemon = false
					showError(t('api_gateway_framework', 'Error while deleting daemon connection'))
				})
		},
		showDaemonModal() {
			emit('edit_daemon', this.daemon)
		},
	},
}
</script>
