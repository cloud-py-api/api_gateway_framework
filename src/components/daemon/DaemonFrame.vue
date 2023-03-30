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
	<NcModal :show="showDaemonFrameModal"
		:title="t('api_gateway_framework', 'Daemon frame')"
		size="full"
		:close-button-contained="false"
		@close="onClose">
		<iframe frameborder="0"
			scrolling="no"
			:showFullScreen="true"
			:src="url"
			style="width: 100%; height: 100%;" />
	</NcModal>
</template>

<script>
import NcModal from '@nextcloud/vue/dist/Components/NcModal.js'

export default {
	name: 'DaemonFrame',
	components: {
		NcModal,
	},
	props: {
		showDaemonFrameModal: {
			type: Boolean,
			required: true,
			default: false,
		},
		url: {
			type: String,
			required: true,
		},
	},
	data() {
		return {
		}
	},
	computed: {
	},
	beforeMount() {
	},
	methods: {
		onClose() {
			this.$emit('update:showDaemonFrameModal', false)
		},
	},
}
</script>
