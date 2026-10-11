from contextlib import contextmanager, AbstractContextManager
from unittest import mock

import pytest
from urllib3 import HTTPConnectionPool
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError

from lektor_project_data import ProjectDataPlugin


@pytest.fixture(scope="session")
def env():
    return mock.Mock(name="Environment")  # bogus but sufficient


@pytest.fixture
def plugin(env):
    return ProjectDataPlugin(env, "project-data")


@contextmanager
def fake_connection_failure():
    """Fake one connection failures."""
    patcher = mock.patch.object(HTTPConnectionPool, "_get_conn")

    def side_effect(*_args, **_kwargs):
        patcher.stop()
        raise ConnectionError

    get_conn = patcher.start()
    get_conn.side_effect = side_effect
    try:
        yield
    finally:
        patcher.stop()


def test_package_data(plugin):
    data = plugin.package_data("lektor-webpack-support")
    assert data["home_page"] == "https://github.com/lektor/lektor-webpack-support"


def test_package_data_retries_on_connect_error(plugin):
    with fake_connection_failure():
        data = plugin.package_data("lektor-webpack-support")
    assert data["home_page"] == "https://github.com/lektor/lektor-webpack-support"
