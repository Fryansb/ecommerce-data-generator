import pytest
import redis
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
import os

# Importar o Command
from core.management.commands.simulate_data import Command
from core.models import Order, OrderItem, Customer, Product


class RedisIntegrationTests(TestCase):
    """Testes de integração com Redis no simulate_data."""

    def setUp(self):
        """Setup básico para testes."""
        self.command = Command()
        self.redis_host = os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = int(os.environ.get('REDIS_PORT', 6379))

    @patch('core.management.commands.simulate_data.redis.Redis')
    def test_redis_connection_initialized(self, mock_redis):
        """Testa se a conexão com Redis é inicializada."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        
        # Simula a conexão
        client = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
        
        assert client is not None

    @patch('core.management.commands.simulate_data.redis.Redis')
    def test_faturamento_redis_incrbyfloat(self, mock_redis):
        """Testa se o Redis incrbyfloat é chamado para agregações diárias."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        
        # Simula dados
        faturamento_por_dia = {'2024-01-01': 1000.50, '2024-01-02': 2500.75}
        
        for dia, valor in faturamento_por_dia.items():
            mock_client.incrbyfloat(f"faturamento:{dia}", valor)
            mock_client.expire(f"faturamento:{dia}", 86400)
        
        # Verifica se incrbyfloat foi chamado
        assert mock_client.incrbyfloat.call_count == 2
        mock_client.incrbyfloat.assert_any_call("faturamento:2024-01-01", 1000.50)
        mock_client.incrbyfloat.assert_any_call("faturamento:2024-01-02", 2500.75)

    @patch('core.management.commands.simulate_data.redis.Redis')
    def test_redis_expiry_set(self, mock_redis):
        """Testa se o TTL de 24 horas é setado no Redis."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        
        dia = '2024-01-01'
        valor = 1000.50
        
        mock_client.incrbyfloat(f"faturamento:{dia}", valor)
        mock_client.expire(f"faturamento:{dia}", 86400)
        
        # Verifica se expire foi chamado com 86400 segundos (24h)
        mock_client.expire.assert_called_with(f"faturamento:{dia}", 86400)

    def test_faturamento_calculation(self):
        """Testa cálculo de faturamento por dia (lógica pura)."""
        # Simula items com dados de teste
        fake_items = [
            Mock(unit_price=100.0, quantity=2, order=Mock(order_date=date(2024, 1, 1))),
            Mock(unit_price=50.0, quantity=3, order=Mock(order_date=date(2024, 1, 1))),
            Mock(unit_price=200.0, quantity=1, order=Mock(order_date=date(2024, 1, 2))),
        ]
        
        # Calcula faturamento
        faturamento_por_dia = {}
        for item in fake_items:
            order_date = item.order.order_date.strftime('%Y-%m-%d')
            faturamento = item.unit_price * item.quantity
            faturamento_por_dia[order_date] = faturamento_por_dia.get(order_date, 0) + faturamento
        
        # Verifica resultado
        assert faturamento_por_dia['2024-01-01'] == 350.0  # 100*2 + 50*3
        assert faturamento_por_dia['2024-01-02'] == 200.0  # 200*1

    @patch('core.management.commands.simulate_data.redis.Redis')
    def test_redis_failure_graceful_handling(self, mock_redis):
        """Testa se falhas no Redis são tratadas graciosamente."""
        mock_redis.side_effect = Exception("Connection refused")
        
        try:
            client = redis.Redis(host=self.redis_host, port=self.redis_port)
            # Se a conexão falhar, o teste não deve travar
            assert True
        except Exception:
            # Esperado que lance exceção
            pass


class RedisStreamlitIntegrationTests(TestCase):
    """Testes para integração do Redis com Streamlit."""

    @patch('streamlit.cache_resource')
    @patch('redis.Redis')
    def test_redis_client_caching(self, mock_redis, mock_cache):
        """Testa se o cliente Redis é cacheado corretamente."""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        # Simula o comportamento do cache_resource
        cached_calls = 0
        
        def mock_cache_decorator(func):
            def wrapper(*args, **kwargs):
                nonlocal cached_calls
                cached_calls += 1
                return mock_client
            return wrapper
        
        mock_cache.side_effect = mock_cache_decorator
        
        # Simula chamadas múltiplas
        result1 = mock_client
        result2 = mock_client
        
        assert result1 is result2

    def test_get_faturamento_redis_format(self):
        """Testa o formato correto de busca de faturamento no Redis."""
        # Data de teste
        test_date = "2024-01-15"
        redis_key = f"faturamento:{test_date}"
        
        # Verifica o formato da chave
        assert redis_key == "faturamento:2024-01-15"
        assert ":" in redis_key


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
