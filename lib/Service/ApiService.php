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

namespace OCA\CloudApiGateway\Service;

use OCP\AppFramework\Db\DoesNotExistException;
use OCP\AppFramework\Db\MultipleObjectsReturnedException;
use OCP\Http\Client\IClient;
use OCP\Http\Client\IClientService;

use OCA\CloudApiGateway\Db\Daemon;
use OCA\CloudApiGateway\Db\DaemonMapper;
use OCP\IURLGenerator;

class ApiService {
	/** @var IClient */
	private $client;

	/** @var IURLGenerator */
	private $urlGenerator;

	/** @var DaemonMapper */
	private $daemonMapper;

	public function __construct(
		IClientService $clientService,
		IURLGenerator $urlGenerator,
		DaemonMapper $daemonMapper,
	) {
		$this->client = $clientService->newClient();
		$this->urlGenerator = $urlGenerator;
		$this->daemonMapper = $daemonMapper;
	}

	public function getDaemons(): array {
		return $this->daemonMapper->findAll();
	}

	public function getDaemon(int $daemonId): ?Daemon {
		try {
			return $this->daemonMapper->find($daemonId);
		} catch (DoesNotExistException | MultipleObjectsReturnedException $e) {
			return null;
		}
	}

	public function getDaemonByName(string $daemonName): ?Daemon {
		try {
			return $this->daemonMapper->findByName($daemonName);
		} catch (DoesNotExistException | MultipleObjectsReturnedException $e) {
			return null;
		}
	}

	public function deleteDaemon(int $daemonId): ?Daemon {
		$daemon = $this->getDaemon($daemonId);
		if ($daemon instanceof Daemon) {
			$this->daemonMapper->delete($daemon);
			return $daemon;
		}
		return null;
	}

	public function updateDaemon(int $daemonId, array $daemonConfig): ?Daemon {
		$daemon = $this->getDaemon($daemonId);
		if ($daemon instanceof Daemon) {
			$daemon->setType($daemonConfig['type']);
			$daemon->setName($daemonConfig['name']);
			$config = [
				'protocol' => $daemonConfig['protocol'],
				'host' => $daemonConfig['host'],
				'port' => $daemonConfig['port'],
				'xAuth' => $daemonConfig['xAuth'],
			];
			$daemon->setConfig(json_encode($config));
			$daemon = $this->daemonMapper->update($daemon);
			return $daemon;
		}
		return null;
	}

	public function saveNewDaemonConnection(array $daemonConfig) {
		$daemon = new Daemon();
		$daemon->setType($daemonConfig['type']);
		$daemon->setName($daemonConfig['name']);
		$config = [
			'protocol' => $daemonConfig['protocol'],
			'host' => $daemonConfig['host'],
			'port' => $daemonConfig['port'],
			'xAuth' => $daemonConfig['xAuth'],
		];
		$daemon->setConfig(json_encode($config));
		$daemon = $this->daemonMapper->insert($daemon);
		return $daemon;
	}

	public function setDaemonOption(Daemon $daemon, string $app, string $option, $value) {
		$response = $this->client->post($this->getDaemonUrl($daemon) . '/option', [
			'json' => [
				'app_name' => $app,
				'key' => $option,
				'value' => $value,
			],
			'headers' => [
				'Authorization' => 'Basic ' . base64_encode($this->getDaemonXAuth($daemon)),
			],
		]);
		return $response;
	}

	public function getDaemonUrl(Daemon $daemon): ?string {
		if ($daemon !== null) {
			$daemonConfig = json_decode($daemon->getConfig(), true);
			return $daemonConfig['protocol'] . '://' . $daemonConfig['host'] . ':' . $daemonConfig['port'];
		}
		return null;
	}

	public function getDaemonXAuth(Daemon $daemon) {
		if ($daemon !== null) {
			$daemonConfig = json_decode($daemon->getConfig(), true);
			return $daemonConfig['xAuth'];
		}
		return null;
	}

	public function runDaemonApp(Daemon $daemon, string $app) {
		$url = $this->getDaemonUrl($daemon) . '/app-run';
		$userToken = 'admin:admin'; // TODO: Change to app password generation
		$ncUrl = $this->urlGenerator->getAbsoluteURL('');
		$response = $this->client->post($url, [
			'json' => [
				'app_name' => $app,
				'user_token' => $userToken,
				'nc_url' => $ncUrl,
			],
			'headers' => [
				'Authorization' => 'Basic ' . base64_encode($this->getDaemonXAuth($daemon)),
			]
		]);
		return $response;
	}
}
