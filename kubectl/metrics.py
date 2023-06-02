"""Performance Measurement for Python Web Frameworks"""
import time
from functools import wraps
from typing import Callable

import psutil
import requests

from .models import MetricsModel, MetricsSchema


def metrics_stateless(endpoint_func):
    """Decorator for performance testing, calculates the system resources utilized by an API Call,
    the network speed and latency, and adds them to the response headers."""

    @wraps(endpoint_func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        cpu_cycles_start = psutil.cpu_count()
        memory_start = psutil.Process().memory_info().rss
        network_start = time.time()

        response = await endpoint_func(*args, **kwargs)

        network_time = time.time() - network_start
        latency = time.time() - start_time
        cpu_cycles_end = psutil.cpu_count()
        memory_end = psutil.Process().memory_info().rss

        cpu_cycle = cpu_cycles_end - cpu_cycles_start
        memory = memory_end - memory_start

        # Calculate network speed (optional)
        # Make a sample request to a test URL and measure the time taken
        test_url = "https://example.com"
        test_start = time.perf_counter()
        _ = requests.get(test_url, timeout=5)
        test_end = time.perf_counter()
        network_speed = len(_.content) / (test_end - test_start)

        # Add metrics to the response headers
        response.headers[
            "x-metrics"
        ] = f"latency={latency},cpu_cycle={cpu_cycle},memory={memory}B,network_time={network_time},network_speed={network_speed},requests_per_second={1/latency}"

        return response

    return wrapper


def metrics_sync(endpoint_func):
    """Decorator for performance testing, calculates the system resources utilized by an API Call,
    the network speed and latency, and adds them to the response headers."""

    @wraps(endpoint_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        cpu_cycles_start = psutil.cpu_count()
        memory_start = psutil.Process().memory_info().rss
        network_start = time.time()
        response = endpoint_func(*args, **kwargs)
        # Network Time Test
        network_time = time.time() - network_start
        # Latency Test
        latency = time.time() - start_time
        cpu_cycles_end = psutil.cpu_count()
        memory_end = psutil.Process().memory_info().rss
        # CPU Test
        cpu_cycle = cpu_cycles_end - cpu_cycles_start
        # Memory Test
        memory = memory_end - memory_start
        # Network Speed Test
        test_start = time.time()
        test_url = "https://example.com"
        requests.get(test_url, timeout=5)
        test_end = time.time()
        network_speed = len(response.content) / (test_end - test_start)
        # Adding metrics to response headers
        response.headers[
            "x-metrics"
        ] = f"latency={latency},cpu_cycle={cpu_cycle},memory={memory}B,network_time={network_time},network_speed={network_speed},requests_per_second={1/latency}"
        return response

    return wrapper


def metrics_stateful(endpoint_func):
    """Decorator that while gathering the metrics from the request, also stores them in a database."""

    @wraps(endpoint_func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        cpu_cycles_start = psutil.cpu_count()
        memory_start = psutil.Process().memory_info().rss
        network_start = time.time()

        response = await endpoint_func(*args, **kwargs)

        network_time = time.time() - network_start
        latency = time.time() - start_time
        cpu_cycles_end = psutil.cpu_count()
        memory_end = psutil.Process().memory_info().rss

        cpu_cycle = cpu_cycles_end - cpu_cycles_start
        memory = memory_end - memory_start

        # Calculate network speed (optional)
        # Make a sample request to a test URL and measure the time taken
        test_url = "https://example.com"
        test_start = time.perf_counter()
        _ = requests.get(test_url, timeout=5)
        test_end = time.perf_counter()
        network_speed = len(_.content) / (test_end - test_start)

        # Add metrics to the response headers
        response.headers[
            "x-metrics"
        ] = f"latency={latency},cpu_cycle={cpu_cycle},memory={memory}B,network_time={network_time},network_speed={network_speed},requests_per_second={1/latency}"

        # Store metrics in the database
        schema = MetricsSchema(
            latency=latency,
            cpu_cycle=cpu_cycle,
            memory=memory,
            network_time=network_time,
            network_speed=network_speed,
            requests_per_second=1 / latency,
        )

        model = MetricsModel(
            metrics=schema,
            endpoint=endpoint_func.__name__,
            method="GET",
            timestamp=time.time(),
        )
        await model.save()
        return response

    return wrapper

