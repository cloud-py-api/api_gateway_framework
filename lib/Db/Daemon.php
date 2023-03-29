<?php

declare(strict_types=1);

/**
 * @copyright Copyright (c) 2022-2023 Andrey Borysenko <andrey18106x@gmail.com>
 *
 * @copyright Copyright (c) 2022-2023 Alexander Piskun <bigcat88@icloud.com>
 *
 * @author 2022-2023 Andrey Borysenko <andrey18106x@gmail.com>
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

namespace OCA\CloudApiGateway\Db;

use JsonSerializable;
use OCP\AppFramework\Db\Entity;

/**
 * Class Daemon
 *
 * @package OCA\CloudApiGateway\Db
 *
 * @method string getName()
 * @method string getType()
 * @method string getConfig()
 * @method void setName(string $name)
 * @method void setType(string $type)
 * @method void setConfig(string $config)
 */
class Daemon extends Entity implements JsonSerializable {
	protected $name;
	protected $type;
	protected $config;

	/**
	 * @param array $params
	 */
	public function __construct(array $params = []) {
		if (isset($params['id'])) {
			$this->setId($params['id']);
		}
		if (isset($params['name'])) {
			$this->setName($params['name']);
		}
		if (isset($params['type'])) {
			$this->setName($params['type']);
		}
		if (isset($params['config'])) {
			$this->setValue($params['config']);
		}
	}

	public function jsonSerialize(): array {
		return [
			'id' => $this->getId(),
			'type' => $this->getType(),
			'name' => $this->getName(),
			'config' => $this->getConfig(),
		];
	}
}
