from prometheus_client import Summary, Gauge

LATENCY = Summary('response_latency', 'Agent response latency')
ERROR_RATE = Gauge('error_rate', 'Last minute error rate')

def track_request():
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                LATENCY.observe(time.time() - start)
                return result
            except Exception:
                ERROR_RATE.inc()
                raise
        return wrapper
    return decorator