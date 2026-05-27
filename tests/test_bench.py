from bench.throughput import run_batch


def test_run_batch_handles_every_request():
    result = run_batch(12)
    assert result["requests"] == 12
    assert result["requests_per_second"] > 0
