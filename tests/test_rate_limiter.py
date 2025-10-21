"""
Tests for Rate Limiter
"""

import pytest
import time
from src.utils.rate_limiter import (
    TokenBucket, BinanceRateLimiter,
    get_rate_limiter, reset_rate_limiter
)
from utils.exceptions import APIException


class TestTokenBucket:
    """Test TokenBucket algorithm"""

    def test_init(self):
        """Test initialization"""
        bucket = TokenBucket(capacity=100, refill_rate=10)
        assert bucket.capacity == 100
        assert bucket.refill_rate == 10
        assert bucket.tokens == 100

    def test_consume_available(self):
        """Test consuming available tokens"""
        bucket = TokenBucket(capacity=10, refill_rate=2)
        result = bucket.consume(5, wait=False)
        assert result is True
        assert bucket.tokens == 5

    def test_consume_wait(self):
        """Test waiting for tokens"""
        bucket = TokenBucket(capacity=10, refill_rate=5)
        # Consume all
        bucket.consume(10, wait=False)
        assert bucket.tokens == 0

        # Wait for refill
        start = time.time()
        result = bucket.consume(3, wait=True)
        elapsed = time.time() - start

        assert result is True
        assert elapsed >= 0.5  # 3 tokens / 5 per second = 0.6s

    def test_consume_no_wait(self):
        """Test not waiting when insufficient"""
        bucket = TokenBucket(capacity=10, refill_rate=2)
        bucket.consume(10, wait=False)
        result = bucket.consume(5, wait=False)
        assert result is False

    def test_consume_exceeds_capacity(self):
        """Test error when requesting more than capacity"""
        bucket = TokenBucket(capacity=10, refill_rate=2)
        with pytest.raises(APIException):
            bucket.consume(15, wait=False)

    def test_refill(self):
        """Test token refill over time"""
        bucket = TokenBucket(capacity=10, refill_rate=10)
        bucket.consume(10, wait=False)
        assert bucket.tokens == 0

        time.sleep(0.5)
        bucket._refill()
        assert bucket.tokens >= 4  # 10 tokens/sec * 0.5s


class TestBinanceRateLimiter:
    """Test Binance-specific rate limiter"""

    def test_init(self):
        """Test initialization"""
        limiter = BinanceRateLimiter()
        assert limiter.weight_bucket.capacity == 1200
        assert limiter.order_bucket.capacity == 20
        assert limiter.daily_order_limit == 100000

    def test_endpoint_weights(self):
        """Test endpoint weight mapping"""
        limiter = BinanceRateLimiter()
        assert limiter._get_endpoint_weight('klines') == 2
        assert limiter._get_endpoint_weight('ticker/24hr') == 40
        assert limiter._get_endpoint_weight('unknown') == 1

    def test_consume_weight(self):
        """Test weight consumption"""
        limiter = BinanceRateLimiter(weight_limit=10, weight_window=5)
        result = limiter.consume_weight('klines', wait=False)
        assert result is True
        assert len(limiter.request_history) == 1

    def test_consume_order(self):
        """Test order consumption"""
        limiter = BinanceRateLimiter(order_limit=5, order_window=5)
        result = limiter.consume_order(wait=False)
        assert result is True
        assert len(limiter.daily_orders) == 1

    def test_daily_order_limit(self):
        """Test daily order limit enforcement"""
        limiter = BinanceRateLimiter(daily_order_limit=3)

        # Consume 3 orders
        for _ in range(3):
            limiter.consume_order(wait=False)

        # 4th should raise exception
        with pytest.raises(APIException):
            limiter.consume_order(wait=False)

    def test_get_stats(self):
        """Test statistics retrieval"""
        limiter = BinanceRateLimiter()
        stats = limiter.get_stats()
        
        assert 'weight_available' in stats
        assert 'order_available' in stats
        assert 'daily_orders' in stats
        assert stats['weight_capacity'] == 1200


class TestGlobalLimiter:
    """Test global rate limiter singleton"""

    def test_get_rate_limiter(self):
        """Test getting global limiter"""
        reset_rate_limiter()
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is limiter2  # Same instance

    def test_reset_rate_limiter(self):
        """Test resetting global limiter"""
        limiter1 = get_rate_limiter()
        reset_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is not limiter2  # Different instance


class TestRateLimitIntegration:
    """Integration tests"""

    def test_multiple_requests(self):
        """Test handling multiple requests"""
        limiter = BinanceRateLimiter(weight_limit=20, weight_window=5)
        
        # Make multiple requests
        for i in range(5):
            result = limiter.consume_weight('klines', wait=False)
            assert result is True
        
        # Should still have capacity
        stats = limiter.get_stats()
        assert stats['weight_available'] >= 0

    def test_rate_limit_recovery(self):
        """Test recovery after rate limit"""
        limiter = BinanceRateLimiter(weight_limit=50, weight_window=2)
        
        # Exhaust limit
        limiter.consume_weight('ticker/24hr', wait=False)  # 40 weight
        
        stats_before = limiter.get_stats()
        assert stats_before['weight_available'] < 50
        
        # Wait for refill
        time.sleep(2)
        
        stats_after = limiter.get_stats()
        assert stats_after['weight_available'] >= \
            stats_before['weight_available']
