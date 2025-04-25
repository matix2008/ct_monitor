"""monitor/notifier.py - Уведомитель для Telegram"""

from typing import List
from typing import Any, Coroutine
import signal
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
from monitor.incident_manager import Incident, IncidentManager
from monitor.notifier import Notifier

class TelegramNotifier(Notifier):
    """
    Уведомляет пользователей о событиях мониторинга через Telegram.
    Поддерживает команды с фильтрацией по ролям.
    """

    def __init__(self, token: str, users: List[dict], incidents: IncidentManager, logger=None):
        """
        Инициализирует TelegramNotifier.

        :param token: токен Telegram-бота
        :param users: список пользователей с их ID, именем и ролью
        :param incidents: экземпляр IncidentManager
        :param logger: необязательный логгер
        """
        self.token = token
        self.incidents = incidents
        self.logger = logger or logging.getLogger(__name__)

        self.users = {
            user["telegram_id"]: {
                "name": user["name"],
                "role": user.get("role", "Spectator")
            }
            for user in users
        }

        self.app = Application.builder().token(self.token).build()

        # Команды
        self.app.add_handler(CommandHandler("start", self.start_handler))
        self.app.add_handler(CommandHandler("shutdown", self.shutdown_handler))
        self.app.add_handler(CommandHandler("help", self.help_handler))
        self.app.add_handler(CommandHandler("status", self.status_handler))
        self.app.add_handler(CommandHandler("refresh", self.refresh_handler))
        self.app.add_handler(CommandHandler("whoami", self.whoami_handler))
        # Добавим обработчик для всех неизвестных команд
        self.app.add_handler(MessageHandler(filters.COMMAND, self.unknown_command_handler))

    def start(self):
        """Запускает Telegram-бота в режиме polling."""
        self.logger.info("Запуск Telegram-бота...")
        self.app.run_polling(stop_signals={signal.SIGINT, signal.SIGTERM})

    def get_user_role(self, user_id: int) -> str:
        """
        Возвращает роль пользователя по его Telegram ID.

        :param user_id: Telegram ID пользователя
        :return: строка с ролью (Admin, Auditor, Spectator и т. д.)
        """
        return self.users.get(user_id, {}).get("role", "None")

    def is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь администратором."""
        return self.get_user_role(user_id) == "Admin"

    def is_admin_or_auditor(self, user_id: int) -> bool:
        """Проверяет, имеет ли пользователь доступ как Auditor или Admin."""
        return self.get_user_role(user_id) in {"Admin", "Auditor"}

    async def start_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Команда /start — приветственное сообщение."""
        await update.message.reply_text(
            "👋 Привет! Я бот мониторинга. Используй /help, чтобы увидеть команды.")

    async def shutdown_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Команда /shutdown — завершение работы монитора."""
        user_id = update.effective_user.id
        if self.is_admin(user_id):
            await update.message.reply_text("ℹ️ Завершаю работу...")
            self.app.stop_running() # останавливаем бота и ... монитор
        else:
            await update.message.reply_text("⛔ Только для администратора.")

    async def help_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Команда /help — список доступных команд и краткая справка."""
        await update.message.reply_text(
            "🛠 Доступные команды:\n"
            "/start — приветствие\n"
            "/help — показать справку\n"
            "/whoami — ваш Telegram ID и роль\n"
            "/status — текущие инциденты (Admin/Auditor)\n"
            "/refresh — перечитать журнал (Admin)\n"
            "/shutdown — завершить работу монитора (Admin)"
        )

    async def whoami_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Команда /whoami — возвращает Telegram ID и роль пользователя."""
        user = update.effective_user
        role = self.get_user_role(user.id)
        msg = f"👤 Вы: {user.full_name}\n🆔 Telegram ID: {user.id}\n🔐 Роль: {role}"
        await update.message.reply_text(msg)

    async def status_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """
        Команда /status — показывает текущие активные инциденты.
        Доступно только Admin и Auditor.
        """
        user_id = update.effective_user.id
        if not self.is_admin_or_auditor(user_id):
            await update.message.reply_text("⛔ Только для ролей Admin и Auditor.")
            return

        active = self.incidents.get_active()
        if not active:
            await update.message.reply_text("✅ Активных инцидентов нет.")
        else:
            report = "\n".join(f"⚠️ {i.resource_name} (с {i.start_time})" for i in active)
            await update.message.reply_text(f"Активные инциденты:\n{report}")

    async def refresh_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """
        Команда /refresh — перечитывает журнал инцидентов из файла.
        Доступно только Admin.
        """
        user_id = update.effective_user.id
        if not self.is_admin(user_id):
            await update.message.reply_text("⛔ Только для администратора.")
            return

        self.incidents.reload_active_incidents()
        await update.message.reply_text("🔄 Инциденты перечитаны из журнала.")

    async def unknown_command_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает неизвестные команды."""
        await update.message.reply_text("⛔ Неизвестная команда. \
                                        Используйте /help для списка доступных.")

    async def notify_incident(self, incident: Incident):
        """
        Уведомляет всех пользователей о начале инцидента.

        :param resource_name: имя ресурса, у которого зафиксирована проблема
        """
        for user_id in self.users:
            try:
                await self.app.bot.send_message(chat_id=user_id, text=f"❗ Инцидент: {incident}")
            except TelegramError as e:
                self.logger.warning("Ошибка при отправке уведомления: %s", e)

    async def notify_recovery(self, incident: Incident):
        """
        Уведомляет всех пользователей о завершении инцидента.

        :param resource_name: имя ресурса, восстановившего работу
        """
        for user_id in self.users:
            try:
                await self.app.bot.\
                    send_message(chat_id=user_id, text=f"✅ Восстановление: {incident}")
            except TelegramError as e:
                self.logger.warning("Ошибка при отправке уведомления: %s", e)

    async def notify_info(self, message: str):
        """
        Уведомляет только Admin и Auditor о системных событиях (запуск, остановка и т.д.).

        :param message: текст сообщения
        """
        for user_id, info in self.users.items():
            if info["role"] in {"Admin", "Auditor"}:
                try:
                    await self.app.bot.send_message(chat_id=user_id, text=f"ℹ️ {message}")
                except TelegramError as e:
                    self.logger.warning("Ошибка при отправке системного уведомления: %s", e)

    def send_task(self, coro: Coroutine[Any, Any, Any]):
        """
        Запускает coroutine в loop'e Telegram-приложения из другого потока
        с помощью job_queue (рекомендовано PTB).
        """
        if self.app and self.app.job_queue:
            self.app.job_queue.run_once(lambda _: self.app.create_task(coro), when=1)
        else:
            self.logger.warning("JobQueue не готов — не удалось отправить coroutine.")
