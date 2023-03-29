<?php
/**
 * @copyright Copyright (c) 2023 Andrey Borysenko <andrey18106x@gmail.com>
 *
 * @copyright Copyright (c) 2023 Alexander Piskun <bigcat88@icloud.com>
 *
 * @author 2023 Andrey Borysenko <andrey18106x@gmail.com>
 *
 * @license AGPL-3.0-or-later
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

return [
	'routes' => [
		// Daemons API actions
		['name' => 'api#checkDaemonsConnection', 'url' => '/daemons-check', 'verb' => 'POST'],
		['name' => 'api#createNewDaemonConnection', 'url' => '/daemon', 'verb' => 'POST'],
		['name' => 'api#getDaemonInfo', 'url' => '/daemon/{daemonId}', 'verb' => 'GET'],
		['name' => 'api#updateDaemonInfo', 'url' => '/daemon/{daemonId}', 'verb' => 'PUT'],
		['name' => 'api#getDaemonInfoByName', 'url' => '/daemon/name/{daemonName}', 'verb' => 'GET'],
		['name' => 'api#runDaemonApp', 'url' => '/daemon/run', 'verb' => 'POST'],
		['name' => 'api#checkDaemonConnectionByName', 'url' => '/daemon/name/{daemonName}/status', 'verb' => 'GET'],
		['name' => 'api#deleteDaemonConnection', 'url' => '/daemon/{daemonId}', 'verb' => 'DELETE'],
		['name' => 'api#checkDaemonConnection', 'url' => '/daemon/{daemonId}/status', 'verb' => 'GET'],
		['name' => 'api#checkDaemonConfig', 'url' => '/daemon/{daemonId}/config-check', 'verb' => 'POST'],
		['name' => 'api#handleNotification', 'url' => '/daemon/{daemonId}/notify', 'verb' => 'POST'],
	]
];
