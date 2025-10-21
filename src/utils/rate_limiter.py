"""
BiX TradeBOT - Rate Limiter
============================
Token Bucket algorithm for API rate limiting protection.

Binance API Limits:
- 1200 weight per minute (rolling window)
- 20 orders per 10 seconds
- 100,000 orders per 24 hours

Author: SALMAN ThinkTank AI Core
Version: 1.0.0
"""

import time
import threading
from collections import deque
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from utils.advanced_logger import get_logger
from utils.exceptions import APIException

logger = get_logger(__name__, component='RateLimiter')


class TokenBucket:
    """
    Token Bucket algorithm implementation for rate limiting.
    
    Tokens are added at a constant rate.
    Each request consumes tokens.
    If no tokens available, request waits or fails.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize Token Bucket.
        
        Args:
            capacity: Maximum tokens (burst size)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

        logger.info(
            f"TokenBucket initialized: "
            f"capacity={capacity}, rate={refill_rate}/s"
        )

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Calculate new tokens
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def consume(self, tokens: int = 1, wait: bool = True) -> bool:
        """
        Consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            wait: If True, wait for tokens. If False, return immediately
            
        Returns:
            True if tokens consumed, False if not available and wait=False
            
        Raises:
            APIException: If tokens > capacity
        """
        if tokens > self.capacity:
            raise APIException(
                f"Requested {tokens} tokens exceeds capacity {self.capacity}"
            )

        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                logger.debug(
                    f"Consumed {tokens} tokens, "
                    f"remaining: {self.tokens:.2f}"
                )
                return True

            if not wait:
                logger.warning(
                    f"Insufficient tokens: need {tokens}, "
                    f"have {self.tokens:.2f}"
                )
                return False

            # Calculate wait time
            needed = tokens - self.tokens
            wait_time = needed / self.refill_rate

            logger.warning(
                f"Rate limit: waiting {wait_time:.2f}s "
                f"for {tokens} tokens"
            )

        # Release lock while waiting
        time.sleep(wait_time)

        # Re-acquire and consume
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                # This shouldn't happen, but handle it
                logger.error("Failed to consume tokens after waiting")
                return False

    def get_available(self) -> float:
        """Get current available tokens"""
        with self.lock:
            self._refill()
            return self.tokens


class BinanceRateLimiter:
    """
    Rate limiter specifically for Binance API.
    
    Implements multiple limits:
    - Weight-based limit (1200/min)
    - Order limit (20/10s, 100k/24h)
    - Request tracking
    """

    # Binance endpoint weights (common endpoints)
    ENDPOINT_WEIGHTS = {
        'ticker/price': 2,
        'ticker/24hr': 40,
        'depth': 10,
        'klines': 2,
        'account': 20,
        'order': 1,
        'order/test': 1,
        'openOrders': 40,
        'allOrders': 20,
    }

    def __init__(
        self,
        weight_limit: int = 1200,
        weight_window: int = 60,
        order_limit: int = 20,
        order_window: int = 10,
        daily_order_limit: int = 100000
    ):
        """
        Initialize Binance Rate Limiter.
        
        Args:
            weight_limit: Max weight per window (default: 1200)
            weight_window: Weight window in seconds (default: 60)
            order_limit: Max orders per order_window (default: 20)
            order_window: Order window in seconds (default: 10)
            daily_order_limit: Max orders per day (default: 100000)
        """
        # Weight-based limiter (1200 weight/min)
        self.weight_bucket = TokenBucket(
            capacity=weight_limit,
            refill_rate=weight_limit / weight_window
        )

        # Order limiter (20 orders/10s)
        self.order_bucket = TokenBucket(
            capacity=order_limit,
            refill_rate=order_limit / order_window
        )

        # Daily order tracking
        self.daily_order_limit = daily_order_limit
        self.daily_orders = deque()
        self.daily_lock = threading.Lock()

        # Request history (for analytics)
        self.request_history = deque(maxlen=1000)

        logger.info(
            f"BinanceRateLimiter initialized: "
            f"weight={weight_limit}/{weight_window}s, "
            f"orders={order_limit}/{order_window}s"
        )

    def _clean_daily_orders(self):
        """Remove orders older than 24 hours"""
        cutoff = datetime.now() - timedelta(days=1)
        with self.daily_lock:
            while self.daily_orders and self.daily_orders[0] < cutoff:
                self.daily_orders.popleft()

    def _get_endpoint_weight(self, endpoint: str) -> int:
        """Get weight for an endpoint"""
        # Try exact match
        if endpoint in self.ENDPOINT_WEIGHTS:
            return self.ENDPOINT_WEIGHTS[endpoint]

        # Try partial match
        for key, weight in self.ENDPOINT_WEIGHTS.items():
            if key in endpoint:
                return weight

        # Default weight
        logger.warning(f"Unknown endpoint weight for '{endpoint}', using 1")
        return 1

    def consume_weight(
        self,
        endpoint: str,
        custom_weight: Optional[int] = None,
        wait: bool = True
    ) -> bool:
        """
        Consume weight for an API request.
        
        Args:
            endpoint: API endpoint (e.g., 'klines', 'ticker/price')
            custom_weight: Override default weight
            wait: Wait if limit exceeded
            
        Returns:
            True if request allowed, False otherwise
        """
        weight = custom_weight or self._get_endpoint_weight(endpoint)

        # Record request
        self.request_history.append({
            'timestamp': datetime.now(),
            'endpoint': endpoint,
            'weight': weight
        })

        return self.weight_bucket.consume(weight, wait=wait)

    def consume_order(self, wait: bool = True) -> bool:
        """
        Consume order quota.
        
        Args:
            wait: Wait if limit exceeded
            
        Returns:
            True if order allowed, False otherwise
            
        Raises:
            APIException: If daily limit exceeded
        """
        # Check daily limit
        self._clean_daily_orders()

        with self.daily_lock:
            if len(self.daily_orders) >= self.daily_order_limit:
                raise APIException(
                    f"Daily order limit exceeded: "
                    f"{self.daily_order_limit} orders/24h"
                )

            # Consume from bucket
            if self.order_bucket.consume(1, wait=wait):
                self.daily_orders.append(datetime.now())
                logger.debug(
                    f"Order consumed, daily total: "
                    f"{len(self.daily_orders)}"
                )
                return True

            return False

    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        self._clean_daily_orders()

        return {
            'weight_available': round(self.weight_bucket.get_available(), 2),
            'weight_capacity': self.weight_bucket.capacity,
            'order_available': round(self.order_bucket.get_available(), 2),
            'order_capacity': self.order_bucket.capacity,
            'daily_orders': len(self.daily_orders),
            'daily_limit': self.daily_order_limit,
            'recent_requests': len(self.request_history)
        }


class RateLimitedExecutor:
    """
    Decorator/context manager for rate-limited function execution.
    """

    def __init__(self, rate_limiter: BinanceRateLimiter):
        """
        Initialize executor.
        
        Args:
            rate_limiter: BinanceRateLimiter instance
        """
        self.rate_limiter = rate_limiter

    def execute(
        self,
        func: Callable,
        endpoint: str,
        is_order: bool = False,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with rate limiting.
        
        Args:
            func: Function to execute
            endpoint: API endpoint name
            is_order: True if this is an order request
            *args, **kwargs: Arguments for func
            
        Returns:
            Function result
            
        Raises:
            APIException: If rate limit exceeded and can't wait
        """
        try:
            # Consume weight
            if not self.rate_limiter.consume_weight(endpoint, wait=True):
                raise APIException(
                    f"Rate limit exceeded for endpoint: {endpoint}"
                )

            # Consume order quota if needed
            if is_order:
                if not self.rate_limiter.consume_order(wait=True):
                    raise APIException("Order rate limit exceeded")

            # Execute function
            result = func(*args, **kwargs)

            return result

        except Exception as e:
            logger.error(
                f"Rate-limited execution failed for {endpoint}: {e}",
                exc_info=True
            )
            raise


# Global rate limiter instance (singleton)
_global_limiter: Optional[BinanceRateLimiter] = None


def get_rate_limiter() -> BinanceRateLimiter:
    """
    Get global rate limiter instance (singleton pattern).
    
    Returns:
        BinanceRateLimiter instance
    """
    global _global_limiter

    if _global_limiter is None:
        _global_limiter = BinanceRateLimiter()
        logger.info("Global rate limiter created")

    return _global_limiter


def reset_rate_limiter():
    """Reset global rate limiter (useful for testing)"""
    global _global_limiter
    _global_limiter = None
    logger.info("Global rate limiter reset")


# Decorator for rate-limited functions
def rate_limited(endpoint: str, is_order: bool = False):
    """
    Decorator for rate-limiting API functions.
    
    Usage:
        @rate_limited('klines')
        def fetch_klines(symbol, interval):
            # API call
            pass
    
    Args:
        endpoint: API endpoint name
        is_order: True if this is an order request
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()
            executor = RateLimitedExecutor(limiter)
            return executor.execute(
                func, endpoint, is_order, *args, **kwargs
            )
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test rate limiter
    print("🧪 Testing Rate Limiter\n")

    limiter = BinanceRateLimiter(
        weight_limit=10,  # Low for testing
        weight_window=5,
        order_limit=3,
        order_window=5
    )

    print("📊 Initial Stats:")
    print(limiter.get_stats())

    print("\n🔄 Testing weight consumption:")
    for i in range(5):
        success = limiter.consume_weight('klines', wait=False)
        print(f"  Request {i+1}: {'✅ Success' if success else '❌ Limited'}")
        print(f"  Stats: {limiter.get_stats()}")

    print("\n⏰ Waiting for refill (3s)...")
    time.sleep(3)

    print("📊 Stats after refill:")
    print(limiter.get_stats())

    print("\n✅ Rate Limiter test complete!")
