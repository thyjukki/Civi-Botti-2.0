from unittest import TestCase
from unittest.mock import Mock, patch

from telegram.ext import ConversationHandler

from civbot.commands import cmd_cancel


class TestCancelAll(TestCase):
    @patch('telegram.ReplyKeyboardRemove')
    def test_cancel_all_should_cancel(self, mock_keyboard):
        mock_keyboard.return_value = mock_keyboard
        bot_mock = Mock()
        update_mock = Mock()

        self.assertEqual(ConversationHandler.END, cmd_cancel.cancel_all(bot_mock, update_mock))

        update_mock.message.reply_text.assert_called_with(
            "Canceled",
            reply_markup=mock_keyboard
        )
        mock_keyboard.assert_called()
