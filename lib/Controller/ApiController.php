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

namespace OCA\CloudApiGateway\Controller;

use OCP\IRequest;
use OCP\AppFramework\Controller;
use OCP\AppFramework\Http\JSONResponse;
use OCP\Http\Client\IClient;
use OCP\Http\Client\IClientService;

use OCA\CloudApiGateway\Service\ApiService;
use OCP\AppFramework\Http;
use Psr\Log\LoggerInterface;

class ApiController extends Controller {
	/** @var IClient */
	private $client;

	/** @var ApiService */
	private $apiService;

	/** @var LoggerInterface */
	private $logger;

	/** @var ?string */
	private $userId;

	public function __construct(
		string $appName,
		IRequest $request,
		IClientService $clientService,
		ApiService $apiService,
		LoggerInterface $logger,
		?string $userId,
	) {
		parent::__construct($appName, $request);

		$this->client = $clientService->newClient();
		$this->apiService = $apiService;
		$this->logger = $logger;
		$this->userId = $userId;
	}

	public function checkDaemonsConnection() {
		$daemons = $this->apiService->getDaemons();
		$daemonsStatus = [];
		foreach ($daemons as $daemon) {
			$url = $this->apiService->getDaemonUrl($daemon) . '/status';
			// Request to daemon with Basic auth
			try {
				$response = $this->client->get($url, [
					'headers' => [
						'Authorization' => 'Basic ' . base64_encode($this->apiService->getDaemonXAuth($daemon))
					]
				]);
				if ($response->getStatusCode() === 200) {
					$daemonsStatus[] = [
						'status' => 200,
						'body' => 'OK',
						'daemon' => $daemon
					];
				} else {
					$daemonsStatus[] = [
						'status' => 400,
						'body' => 'Bad request',
						'daemon' => $daemon
					];
				}
			} catch (\Exception $e) {
				$daemonsStatus[] = [
					'status' => 400,
					'body' => 'Bad request',
					'daemon' => $daemon,
					'error' => $e->getMessage()
				];
			}
		}
		return new JSONResponse($daemonsStatus, Http::STATUS_OK);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function checkDaemonConnection(int $daemonId, ?array $daemonConfig): JSONResponse {
		$daemon = $this->apiService->getDaemon($daemonId);
		if ($daemon !== null) {
			// Check daemon connection
			if (!isset($daemonConfig)) {
				$daemonConfig = json_decode($daemon->getConfig(), true);
			}
			$url = $daemonConfig['protocol'] . '://' . $daemonConfig['host'] . ':' . $daemonConfig['port'] . '/status';
			// Request to daemon with Basic auth
			$response = $this->client->get($url, [
				'headers' => [
					'Authorization' => 'Basic ' . base64_encode($daemonConfig['xAuth'])
				]
			]);
			$status = json_decode($response->getBody(), true);
			if ($response->getStatusCode() === 200) {
				return new JSONResponse([
					'status' => 200,
					'body' => 'OK',
					'daemon' => $daemon,
					'daemonStatus' => $status,
				], Http::STATUS_OK);
			}
			return new JSONResponse([
				'status' => 400,
				'body' => 'Bad request'
			], Http::STATUS_BAD_REQUEST);
		}
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function checkDaemonConfig(int $daemonId, ?array $daemonConfig): JSONResponse {
		return $this->checkDaemonConnection($daemonId, $daemonConfig);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function checkDaemonConnectionByName(string $daemonName): JSONResponse {
		$daemon = $this->apiService->getDaemonByName($daemonName);
		if ($daemon !== null) {
			$url = $this->apiService->getDaemonUrl($daemon) . '/status';
			// Request to daemon with Basic auth
			$response = $this->client->get($url, [
				'headers' => [
					'Authorization' => 'Basic ' . base64_encode($this->apiService->getDaemonXAuth($daemon))
				]
			]);
			$status = json_decode($response->getBody(), true);
			if ($response->getStatusCode() === 200) {
				return new JSONResponse([
					'status' => 200,
					'body' => 'OK',
					'daemon' => $daemon,
					'daemonStatus' => $status,
				], Http::STATUS_OK);
			}
			return new JSONResponse([
				'status' => 400,
				'body' => 'Bad request'
			], Http::STATUS_BAD_REQUEST);
		}
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function createNewDaemonConnection(array $daemonConfig): JSONResponse {
		if ($this->apiService->getDaemonByName($daemonConfig['name']) !== null) {
			// Daemon with this name already exists response
			return new JSONResponse([
				'status' => 409,
				'body' => 'Conflict'
			], Http::STATUS_CONFLICT);
		}
		$daemon = $this->apiService->saveNewDaemonConnection($daemonConfig);
		if ($daemon->getId() !== null) {
			// TODO: Add set_option requests to configure daemon
			try {
				$this->apiService->setDaemonOption($daemon, '', 'id', $daemon->getId());
				$this->apiService->setDaemonOption($daemon, '', 'name', $daemon->getName());
			} catch (\Exception $e) {
				$this->logger->error('Error while setting options for new daemon connection: ' . $e->getMessage());
			}
			return new JSONResponse([
				'status' => 200,
				'body' => 'OK',
				'daemon' => $daemon
			], Http::STATUS_OK);
		}
		return new JSONResponse([
			'status' => 400,
			'body' => 'Bad request'
		], Http::STATUS_BAD_REQUEST);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function getDaemonInfo(int $daemonId) {
		$daemon = $this->apiService->getDaemon($daemonId);
		if ($daemon !== null) {
			return new JSONResponse([
				'status' => 200,
				'body' => 'OK',
				'daemon' => $daemon
			], Http::STATUS_OK);
		}
		return new JSONResponse([
			'status' => 404,
			'body' => 'Not found'
		], Http::STATUS_NOT_FOUND);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function updateDaemonInfo(int $daemonId, array $daemonConfig) {
		$daemon = $this->apiService->updateDaemon($daemonId, $daemonConfig);
		if ($daemon !== null) {
			return new JSONResponse([
				'status' => 200,
				'body' => 'OK',
				'daemon' => $daemon
			], Http::STATUS_OK);
		}
		return new JSONResponse([
			'status' => 404,
			'body' => 'Not found'
		], Http::STATUS_NOT_FOUND);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function getDaemonInfoByName(string $daemonName) {
		$daemon = $this->apiService->getDaemonByName($daemonName);
		if ($daemon !== null) {
			return new JSONResponse([
				'status' => 200,
				'body' => 'OK',
				'daemon' => $daemon
			], Http::STATUS_OK);
		}
		return new JSONResponse([
			'status' => 404,
			'body' => 'Not found'
		], Http::STATUS_NOT_FOUND);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function deleteDaemonConnection(int $daemonId): JSONResponse {
		$daemon = $this->apiService->deleteDaemon($daemonId);
		if ($daemon !== null) {
			return new JSONResponse([
				'status' => 200,
				'body' => 'OK',
				'daemon' => $daemon
			], Http::STATUS_OK);
		}
		return new JSONResponse([
			'status' => 404,
			'body' => 'Not found'
		], Http::STATUS_NOT_FOUND);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function handleRedirect(array $params): JSONResponse {
		// Dummy response
		return new JSONResponse([
			'status' => 200,
			'body' => 'OK',
			'params' => $params
		], Http::STATUS_OK);
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function handleNotification(array $params): JSONResponse {
		// Dummy response
		return new JSONResponse([
			'status' => 200,
			'body' => 'OK',
			'params' => $params
		], Http::STATUS_OK);
		// TODO: Handle notification from daemon
	}

	/**
	 * @NoAdminRequired
	 * @NoCSRFRequired
	 */
	public function runDaemonApp(string $app, int $daemonId): JSONResponse {
		$daemon = $this->apiService->getDaemon($daemonId);
		if ($daemon !== null) {
			$appRunResponse = $this->apiService->runDaemonApp($daemon, $app);
			return new JSONResponse([
				'status' => 200,
				'body' => 'OK',
				'daemon' => $daemon,
				'app' => $app,
				'appRunResponse' => $appRunResponse,
			], Http::STATUS_OK);
		}
		return new JSONResponse([
			'status' => 404,
			'body' => 'Not found'
		], Http::STATUS_NOT_FOUND);
	}
}
