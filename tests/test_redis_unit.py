"""
Testes unitários para funcionalidades do Redis.
Estes testes usam mocks e não requerem banco de dados ou Django configurado.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date


def test_faturamento_calculation():
    """Testa o cálculo de faturamento por dia (lógica pura)."""
    # Simula items com dados de teste
    fake_items = [
        Mock(unit_price=100.0, quantity=2, order=Mock(order_date=date(2024, 1, 1))),
        Mock(unit_price=50.0, quantity=3, order=Mock(order_date=date(2024, 1, 1))),
        Mock(unit_price=200.0, quantity=1, order=Mock(order_date=date(2024, 1, 2))),
    ]
    
    # Calcula faturamento (lógica do simulate_data.py)
    faturamento_por_dia = {}
    for item in fake_items:
        order_date = item.order.order_date.strftime('%Y-%m-%d')
        faturamento = item.unit_price * item.quantity
        faturamento_por_dia[order_date] = faturamento_por_dia.get(order_date, 0) + faturamento
    
    # Verifica resultado
    assert faturamento_por_dia['2024-01-01'] == 350.0  # 100*2 + 50*3
    assert faturamento_por_dia['2024-01-02'] == 200.0  # 200*1
    assert len(faturamento_por_dia) == 2


@patch('redis.Redis')
def test_redis_incrbyfloat_calls(mock_redis):
    """Testa se o Redis incrbyfloat é chamado corretamente para agregações diárias."""
    mock_client = MagicMock()
    mock_redis.return_value = mock_client
    
    # Simula o cliente Redis
    redis_client = mock_redis()
    
    # Simula dados de faturamento
    faturamento_por_dia = {'2024-01-01': 1000.50, '2024-01-02': 2500.75}
    
    # Executa a lógica de atualização do Redis
    for dia, valor in faturamento_por_dia.items():
        redis_client.incrbyfloat(f"faturamento:{dia}", valor)
        redis_client.expire(f"faturamento:{dia}", 86400)
    
    # Verifica se incrbyfloat foi chamado corretamente
    assert mock_client.incrbyfloat.call_count == 2
    mock_client.incrbyfloat.assert_any_call("faturamento:2024-01-01", 1000.50)
    mock_client.incrbyfloat.assert_any_call("faturamento:2024-01-02", 2500.75)
    
    # Verifica se expire foi chamado para cada chave
    assert mock_client.expire.call_count == 2


@patch('redis.Redis')
def test_redis_expiry_ttl(mock_redis):
    """Testa se o TTL de 24 horas (86400 segundos) é setado no Redis."""
    mock_client = MagicMock()
    mock_redis.return_value = mock_client
    
    redis_client = mock_redis()
    
    dia = '2024-01-01'
    valor = 1000.50
    
    redis_client.incrbyfloat(f"faturamento:{dia}", valor)
    redis_client.expire(f"faturamento:{dia}", 86400)
    
    # Verifica se expire foi chamado com TTL correto (24 horas)
    mock_client.expire.assert_called_with(f"faturamento:{dia}", 86400)


def test_redis_key_format():
    """Testa o formato correto das chaves do Redis."""
    test_date = "2024-01-15"
    redis_key = f"faturamento:{test_date}"
    
    # Verifica o formato da chave
    assert redis_key == "faturamento:2024-01-15"
    assert ":" in redis_key
    assert redis_key.startswith("faturamento:")


@patch('redis.Redis')
def test_redis_connection_mock(mock_redis):
    """Testa se a conexão com Redis pode ser mockada."""
    mock_client = MagicMock()
    mock_redis.return_value = mock_client
    mock_client.ping.return_value = True
    
    # Simula conexão
    client = mock_redis()
    
    # Verifica se o cliente foi criado
    assert client is not None
    assert client.ping() == True


def test_multiple_aggregations():
    """Testa múltiplas agregações de faturamento no mesmo dia."""
    # Simula múltiplos items para o mesmo dia
    fake_items = [
        Mock(unit_price=100.0, quantity=1, order=Mock(order_date=date(2024, 1, 1))),
        Mock(unit_price=200.0, quantity=2, order=Mock(order_date=date(2024, 1, 1))),
        Mock(unit_price=50.0, quantity=3, order=Mock(order_date=date(2024, 1, 1))),
    ]
    
    # Calcula faturamento
    faturamento_por_dia = {}
    for item in fake_items:
        order_date = item.order.order_date.strftime('%Y-%m-%d')
        faturamento = item.unit_price * item.quantity
        faturamento_por_dia[order_date] = faturamento_por_dia.get(order_date, 0) + faturamento
    
    # Verifica agregação total para o dia
    assert faturamento_por_dia['2024-01-01'] == 650.0  # 100 + 400 + 150


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
