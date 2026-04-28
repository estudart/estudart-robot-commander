from __future__ import annotations

from typing import Optional

from src.application.services.logging_service import LoggingService
from src.application.services.robot_commander import RobotCommander
from src.application.services.robot_worker import RobotWorker
from src.infrastructure.redis_adapter import RedisAdapter
from src.infrastructure.robot_adapter import RobotAdapter


_logging_service: Optional[LoggingService] = None
_redis_adapter: Optional[RedisAdapter] = None
_robot_adapter: Optional[RobotAdapter] = None
_robot_worker: Optional[RobotWorker] = None
_robot_commander: Optional[RobotCommander] = None


def get_logging_service() -> LoggingService:
	global _logging_service
	if not _logging_service:
		_logging_service = LoggingService(name="RobotCommander")
	return _logging_service


def get_redis_adapter() -> RedisAdapter:
	global _redis_adapter
	if not _redis_adapter:
		_redis_adapter = RedisAdapter()
	return _redis_adapter


def get_robot_adapter() -> RobotAdapter:
	global _robot_adapter
	if not _robot_adapter:
		logging_service = get_logging_service()
		_robot_adapter = RobotAdapter(logging_service=logging_service)
	return _robot_adapter


def get_robot_worker() -> RobotWorker:
	global _robot_worker
	if not _robot_worker:
		logging_service = get_logging_service()
		redis_adapter = get_redis_adapter()
		robot_adapter = get_robot_adapter()
		_robot_worker = RobotWorker(
			robot_adapter=robot_adapter,
			redis_adapter=redis_adapter,
			logging_service=logging_service,
		)
	return _robot_worker

def get_robot_commander() -> RobotCommander:
	global _robot_commander
	if not _robot_commander:
		logging_service = get_logging_service()
		redis_adapter = get_redis_adapter()

		_robot_commander = RobotCommander(
			redis_adapter=redis_adapter,
			logging_service=logging_service,
		)

	return _robot_commander