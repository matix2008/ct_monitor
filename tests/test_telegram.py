"""tests/test_telegram.py"""

from unittest.mock import AsyncMock, MagicMock
import pytest
from monitor.telegram_notifier import TelegramNotifier

@pytest.mark.asyncio
async def test_command_whoami_for_admin():
    """
    Проверяет, что команда /whoami для Admin возвращает корректный ответ.
    """
    users = [{"telegram_id": 123, "name": "Test Admin", "role": "Admin"}]
    incidents = MagicMock()
    logger = MagicMock()

    bot = TelegramNotifier(token="FAKE", users=users, incidents=incidents, logger=logger)

    update = MagicMock()
    context = MagicMock()
    update.effective_user.id = 123
    update.effective_user.full_name = "Test Admin"
    update.message.reply_text = AsyncMock()

    await bot.whoami_handler(update, context)

    update.message.reply_text.assert_awaited_with(
        "👤 Вы: Test Admin\n🆔 Telegram ID: 123\n🔐 Роль: Admin"
    )


@pytest.mark.asyncio
async def test_command_status_blocked_for_spectator():
    """
    Проверяет, что пользователь с ролью Spectator не может вызвать /status.
    """
    users = [{"telegram_id": 456, "name": "Guest", "role": "Spectator"}]
    incidents = MagicMock()
    logger = MagicMock()

    bot = TelegramNotifier(token="FAKE", users=users, incidents=incidents, logger=logger)

    update = MagicMock()
    context = MagicMock()
    update.effective_user.id = 456
    update.message.reply_text = AsyncMock()

    await bot.status_handler(update, context)

    update.message.reply_text.assert_awaited()
    args, _ = update.message.reply_text.call_args
    assert "только для ролей" in args[0].lower()


@pytest.mark.asyncio
async def test_command_refresh_only_for_admin():
    """
    Проверяет, что /refresh доступен только Admin-пользователю.
    """
    users = [
        {"telegram_id": 789, "name": "Admin User", "role": "Admin"},
        {"telegram_id": 790, "name": "Auditor User", "role": "Auditor"}
    ]
    incidents = MagicMock()
    logger = MagicMock()

    bot = TelegramNotifier(token="FAKE", users=users, incidents=incidents, logger=logger)

    # Admin
    update = MagicMock()
    context = MagicMock()
    update.effective_user.id = 789
    update.message.reply_text = AsyncMock()

    await bot.refresh_handler(update, context)
    update.message.reply_text.assert_awaited()

    # Auditor (не должен иметь доступ)
    update = MagicMock()
    context = MagicMock()
    update.effective_user.id = 790
    update.message.reply_text = AsyncMock()

    await bot.refresh_handler(update, context)
    args, _ = update.message.reply_text.call_args
    assert "только для администратора" in args[0].lower()


@pytest.mark.asyncio
async def test_notify_incident_sends_to_all_roles():
    """
    Проверяет, что сообщение об инциденте рассылается всем пользователям.
    """
    users = [
        {"telegram_id": 1, "name": "Admin", "role": "Admin"},
        {"telegram_id": 2, "name": "Auditor", "role": "Auditor"},
        {"telegram_id": 3, "name": "Spectator", "role": "Spectator"}
    ]
    bot = TelegramNotifier(token="FAKE", users=users, incidents=MagicMock(), logger=MagicMock())
    bot.app.bot = MagicMock()
    bot.app.bot.send_message = AsyncMock()

    await bot.notify_incident("Test Incident")

    assert bot.app.bot.send_message.await_count == 3
    for uid in [1, 2, 3]:
        called = any(
            call.kwargs["chat_id"] == uid and "❗ Инцидент" in call.kwargs["text"]
            for call in bot.app.bot.send_message.await_args_list
        )
        assert called, f"Message not sent to user {uid}"


@pytest.mark.asyncio
async def test_notify_resolved_sends_to_all_roles():
    """
    Проверяет, что сообщение о завершении инцидента рассылается всем пользователям.
    """
    users = [
        {"telegram_id": 1, "name": "Admin", "role": "Admin"},
        {"telegram_id": 2, "name": "Auditor", "role": "Auditor"},
        {"telegram_id": 3, "name": "Spectator", "role": "Spectator"}
    ]
    bot = TelegramNotifier(token="FAKE", users=users, incidents=MagicMock(), logger=MagicMock())
    bot.app.bot = MagicMock()
    bot.app.bot.send_message = AsyncMock()

    await bot.notify_recovery("Test Resolved")

    assert bot.app.bot.send_message.await_count == 3
    for uid in [1, 2, 3]:
        called = any(
            call.kwargs["chat_id"] == uid and "✅ Восстановление" in call.kwargs["text"]
            for call in bot.app.bot.send_message.await_args_list
        )
        assert called, f"Resolved message not sent to user {uid}"


@pytest.mark.asyncio
async def test_notify_info_sends_only_to_admin_and_auditor():
    """
    Проверяет, что информационное сообщение рассылается только Admin и Auditor.
    """
    users = [
        {"telegram_id": 1, "name": "Admin", "role": "Admin"},
        {"telegram_id": 2, "name": "Auditor", "role": "Auditor"},
        {"telegram_id": 3, "name": "Spectator", "role": "Spectator"}
    ]
    bot = TelegramNotifier(token="FAKE", users=users, incidents=MagicMock(), logger=MagicMock())
    bot.app.bot = MagicMock()
    bot.app.bot.send_message = AsyncMock()

    await bot.notify_info("Test Info")

    assert bot.app.bot.send_message.await_count == 2
    for uid in [1, 2]:
        called = any(
            call.kwargs["chat_id"] == uid and "ℹ️ " in call.kwargs["text"]
            for call in bot.app.bot.send_message.await_args_list
        )
        assert called, f"Info message not sent to user {uid}"

    for uid in [3]:
        not_called = all(
            call.kwargs["chat_id"] != uid for call in bot.app.bot.send_message.await_args_list
        )
        assert not_called, f"Spectator {uid} should not receive info message"
