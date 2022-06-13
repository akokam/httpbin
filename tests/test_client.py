from httpbin import client as candidate


def test_config():
    """SCENARIO: Instantiation of a config
    TEST: No errors
    """
    candidate.Config(base_url="https://some.url")
