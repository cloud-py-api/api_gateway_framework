<?php

declare(strict_types=1);

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

namespace OCA\CloudApiGateway\Migration;

use OCP\DB\ISchemaWrapper;
use OCP\Migration\SimpleMigrationStep;
use OCP\Migration\IOutput;

use OCA\CloudApiGateway\AppInfo\Application;

class Version0001Date20230327114550 extends SimpleMigrationStep {
	/**
	 * @param IOutput $output
	 * @param Closure $schemaClosure The `\Closure` returns a `ISchemaWrapper`
	 * @param array $options
	 * @return null|ISchemaWrapper
	 */
	public function changeSchema(IOutput $output, \Closure $schemaClosure, array $options) {
		/** @var ISchemaWrapper $schema */
		$schema = $schemaClosure();
		$tableNamePrefix = 'cag';

		if (!$schema->hasTable($tableNamePrefix . '_daemons')) {
			$table = $schema->createTable($tableNamePrefix . '_daemons');

			$table->addColumn('id', 'integer', [
				'autoincrement' => true,
				'notnull' => true
			]);
			$table->addColumn('type', 'string', [
				'notnull' => true,
				'default' => ""
			]);
			$table->addColumn('name', 'string', [
				'notnull' => true,
				'default' => ""
			]);
			$table->addColumn('config', 'json', [
				'notnull' => true
			]);

			$table->setPrimaryKey(['id']);
			$table->addUniqueIndex(['name'], $tableNamePrefix . '_daemons_name');
		}

		return $schema;
	}
}
