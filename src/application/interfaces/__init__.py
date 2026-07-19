"""Repository interfaces (ports) for the application layer."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.checkin import CheckIn
from src.domain.entities.goal import Goal
from src.domain.entities.plan import Plan
from src.domain.entities.scheduled_task import ScheduledTask
from src.domain.entities.score_event import ScoreEvent
from src.domain.entities.task_template import TaskTemplate


class IUserRepository(ABC):
    """Foydalanuvchi repository interfeysi."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> dict | None:
        """ID bo'yicha foydalanuvchini topish."""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: str) -> dict | None:
        """Telegram ID bo'yicha foydalanuvchini topish."""

    @abstractmethod
    async def create(self, user_data: dict) -> dict:
        """Yangi foydalanuvchi yaratish."""

    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> dict | None:
        """Foydalanuvchi ma'lumotlarini yangilash."""


class IGoalRepository(ABC):
    """Maqsad repository interfeysi."""

    @abstractmethod
    async def get_by_id(self, goal_id: UUID) -> Goal | None:
        """ID bo'yicha maqsadni topish."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[Goal]:
        """Foydalanuvchining barcha maqsadlarini olish."""

    @abstractmethod
    async def create(self, goal: Goal) -> Goal:
        """Yangi maqsad yaratish."""

    @abstractmethod
    async def update(self, goal_id: UUID, goal_data: dict) -> Goal | None:
        """Maqsad ma'lumotlarini yangilash."""


class IPlanRepository(ABC):
    """Reja repository interfeysi."""

    @abstractmethod
    async def get_by_id(self, plan_id: UUID) -> Plan | None:
        """ID bo'yicha rejani topish."""

    @abstractmethod
    async def get_by_goal_id(self, goal_id: UUID) -> list[Plan]:
        """Maqsadga tegishli barcha rejlarni olish."""

    @abstractmethod
    async def get_active_plan(self, goal_id: UUID) -> Plan | None:
        """Maqsadning faol rejasini olish."""

    @abstractmethod
    async def create(self, plan: Plan) -> Plan:
        """Yangi reja yaratish."""


class ITaskTemplateRepository(ABC):
    """Vazifa shabloni repository interfeysi."""

    @abstractmethod
    async def get_by_id(self, template_id: UUID) -> TaskTemplate | None:
        """ID bo'yicha shablonni topish."""

    @abstractmethod
    async def get_by_plan_id(self, plan_id: UUID) -> list[TaskTemplate]:
        """Rejaga tegishli barcha shablonlarni olish."""

    @abstractmethod
    async def create(self, template: TaskTemplate) -> TaskTemplate:
        """Yangi shablon yaratish."""

    @abstractmethod
    async def update(
        self, template_id: UUID, template_data: dict
    ) -> TaskTemplate | None:
        """Shablon ma'lumotlarini yangilash."""


class IScheduledTaskRepository(ABC):
    """Rejalashtirilgan vazifa repository interfeysi."""

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> ScheduledTask | None:
        """ID bo'yicha vazifani topish."""

    @abstractmethod
    async def get_by_date(self, scheduled_date) -> list[ScheduledTask]:
        """Belgilangan sanadagi barcha vazifalarni olish."""

    @abstractmethod
    async def get_pending_by_date(self, scheduled_date) -> list[ScheduledTask]:
        """Belgilangan sanadagi pending vazifalarni olish."""

    @abstractmethod
    async def create(self, task: ScheduledTask) -> ScheduledTask:
        """Yangi vazifa yaratish."""

    @abstractmethod
    async def update_status(self, task_id: UUID, status: str) -> ScheduledTask | None:
        """Vazifa statusini yangilash."""


class IScoreRepository(ABC):
    """Ball repository interfeysi."""

    @abstractmethod
    async def get_by_checkin_id(self, checkin_id: UUID) -> ScoreEvent | None:
        """Check-in ID bo'yicha ball hodisasini topish."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[ScoreEvent]:
        """Foydalanuvchining barcha ballarini olish."""

    @abstractmethod
    async def create(self, event: ScoreEvent) -> ScoreEvent:
        """Yangi ball hodisasi yaratish."""


class ICheckInRepository(ABC):
    """Check-in repository interfeysi."""

    @abstractmethod
    async def get_by_scheduled_task_id(self, scheduled_task_id: UUID) -> CheckIn | None:
        """Scheduled task ID bo'yicha check-in topish."""

    @abstractmethod
    async def create(self, checkin: CheckIn) -> CheckIn:
        """Yangi check-in yaratish."""


class INotifier(ABC):
    """Xabar berish interfeysi."""

    @abstractmethod
    async def send_notification(self, user_id: UUID, message: str) -> bool:
        """Foydalanuvchiga xabar yuborish."""

    @abstractmethod
    async def send_checkin_reminder(
        self, user_id: UUID, task_title: str, scheduled_time: str
    ) -> bool:
        """Check-in eslatmasi yuborish."""
