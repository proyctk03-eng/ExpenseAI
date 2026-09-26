"""
Kiểm thử tự động cho cơ chế Dự phòng API Key (Failover Multi-Key) cho Google Gemini.
Đảm bảo khi Key 1 bị hết quota / token (lỗi 429 hoặc Resource Exhausted),
hệ thống tự động kích hoạt Key dự phòng để tiếp tục phục vụ người dùng.
"""
import pytest
from unittest.mock import MagicMock, patch
from openai import RateLimitError

from src.config import get_gemini_api_keys
from src.utils.ai_key_manager import GeminiKeyManager
from src.services.ai_advice import AIAdviceService
from src.services.ai_classifier import AIClassifier
from src.services.ai_behavior import AIBehaviorService
from src.services.ai_vision import AIVisionService


class TestGeminiMultiKeyFailover:
    """Kiểm thử tính năng quản lý và xoay vòng nhiều Google Gemini API Keys."""

    def test_get_gemini_api_keys_order_and_uniqueness(self):
        """Kiểm tra thứ tự ưu tiên của danh sách API Keys: Primary -> Backup."""
        keys = get_gemini_api_keys()
        # Trong file .env, ta có cả GEMINI_API_KEY và GEMINI_API_KEY_BACKUP
        assert len(keys) >= 2
        assert keys[0] != keys[1]
        assert isinstance(keys[0], str) and len(keys[0]) > 10
        assert isinstance(keys[1], str) and len(keys[1]) > 10

    def test_key_manager_rotation_and_failover(self):
        """KeyManager phải xoay vòng sang key dự phòng khi key hiện tại hết quota."""
        km = GeminiKeyManager()
        assert km.total_keys >= 2
        initial_key = km.current_key
        assert initial_key == km._keys[0]

        # Mô phỏng Key 1 gặp lỗi quota
        switched = km.mark_current_key_exhausted("429 Resource Exhausted")
        assert switched is True
        assert km.current_key == km._keys[1]
        assert km.current_key != initial_key

        # Nếu tiếp tục hết key thứ 2 (hết sạch keys)
        second_switched = km.mark_current_key_exhausted("429 Quota Exceeded")
        assert second_switched is False

    def test_ai_advice_service_auto_failover_on_rate_limit(self):
        """AIAdviceService phải tự động kích hoạt key dự phòng khi gặp RateLimitError."""
        service = AIAdviceService()
        
        # Mô phỏng provider là gemini
        service._provider = "gemini"
        service.is_available = True
        
        with patch("src.services.ai_advice.gemini_key_manager.mark_current_key_exhausted", return_value=True) as mock_mark:
            with patch("src.services.ai_advice.gemini_key_manager.get_client") as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client
                
                result = service._failover_to_next_client("Rate limit exceeded")
                assert result is True
                assert service.client == mock_client
                mock_mark.assert_called_once()

    def test_ai_classifier_auto_failover_on_rate_limit(self):
        """AIClassifier phải tự động kích hoạt key dự phòng khi gặp RateLimitError."""
        classifier = AIClassifier()
        classifier._provider = "gemini"
        classifier.is_available = True
        
        with patch("src.services.ai_classifier.gemini_key_manager.mark_current_key_exhausted", return_value=True) as mock_mark:
            with patch("src.services.ai_classifier.gemini_key_manager.get_client") as mock_get_client:
                mock_client = MagicMock()
                mock_get_client.return_value = mock_client
                
                result = classifier._failover_to_next_client("429 Too Many Requests")
                assert result is True
                assert classifier.client == mock_client
                mock_mark.assert_called_once()

    def test_ai_behavior_and_vision_failover(self):
        """AIBehaviorService và AIVisionService hỗ trợ failover sang backup key."""
        behavior = AIBehaviorService()
        behavior._provider = "gemini"
        
        with patch("src.services.ai_behavior.gemini_key_manager.mark_current_key_exhausted", return_value=True):
            with patch("src.services.ai_behavior.gemini_key_manager.get_client") as mock_gc:
                mock_gc.return_value = MagicMock()
                assert behavior._failover_to_next_client("429 Quota") is True

        vision = AIVisionService()
        vision._provider = "gemini"
        with patch("src.services.ai_vision.gemini_key_manager.mark_current_key_exhausted", return_value=True):
            with patch("src.services.ai_vision.gemini_key_manager.get_client") as mock_gc:
                mock_gc.return_value = MagicMock()
                assert vision._failover_to_next_client("429 Quota") is True
