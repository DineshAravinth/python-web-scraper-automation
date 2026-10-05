from scraper.proxy_manager import ProxyManager


def test_proxy_rotation():
    proxies = [
        "http://proxy1:8000",
        "http://proxy2:8000",
        "http://proxy3:8000",
    ]

    manager = ProxyManager(proxies)

    assert manager.get_proxy_count() == 3
    assert manager.has_proxies() is True

    assert manager.get_next_proxy() == "http://proxy1:8000"
    assert manager.get_next_proxy() == "http://proxy2:8000"
    assert manager.get_next_proxy() == "http://proxy3:8000"

    # Rotation should start again
    assert manager.get_next_proxy() == "http://proxy1:8000"


def test_proxy_manager_without_proxies():
    manager = ProxyManager()

    assert manager.has_proxies() is False
    assert manager.get_proxy_count() == 0
    assert manager.get_next_proxy() is None


def test_proxy_manager_with_empty_proxy_list():
    manager = ProxyManager([])

    assert manager.has_proxies() is False
    assert manager.get_proxy_count() == 0
    assert manager.get_next_proxy() is None


def test_proxy_rotation_with_single_proxy():
    proxies = [
        "http://proxy1:8000",
    ]

    manager = ProxyManager(proxies)

    assert manager.get_proxy_count() == 1
    assert manager.has_proxies() is True

    assert manager.get_next_proxy() == "http://proxy1:8000"
    assert manager.get_next_proxy() == "http://proxy1:8000"
    assert manager.get_next_proxy() == "http://proxy1:8000"