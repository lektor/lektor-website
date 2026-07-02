import pytest

from lektor.environment import Environment
from lektor.environment import FormatExpression
from lektor.project import Project

from lektor_jinja_globals import JinjaGlobalsPlugin
from lektor_jinja_globals import mailto_link


@pytest.mark.parametrize("email_address, default_link_text, expected", [
    ("joe@example.net", "Joe Blö", '<a href="mailto:joe@example.net">Joe Blö</a>'),
    ("joe@example.net", "Joe & Co", '<a href="mailto:joe@example.net">Joe &amp; Co</a>'),
    ("Joe & Co <joe@example.com>", "", '<a href="mailto:joe@example.com">Joe &amp; Co</a>'),
    ("Joe <joe@example.com>, Mary <mary@example.net>", "", '<a href="mailto:joe@example.com, mary@example.net">Joe, Mary</a>'),
    ("joe@example.net", "", '<a href="mailto:joe@example.net">joe@example.net</a>'),
    ("joe@example.net", None, '<a href="mailto:joe@example.net">joe@example.net</a>'),
    ("", "Goober", ""),
    ("<>", "Goober", ""),
])
def test_mailto_link(email_address, default_link_text, expected):
    assert mailto_link(email_address, default_link_text) == expected


@pytest.fixture
def jinja_globals_env(tmp_path):
    """A minimal Lektor environment with our plugin registered."""
    project = Project("Test Project", project_file=None, tree=tmp_path)
    env = Environment(project, load_plugins=False)
    env.plugin_controller.instanciate_plugin("jinja-globals", JinjaGlobalsPlugin)
    env.plugin_controller.emit("setup-env")
    return env


def test_integration(jinja_globals_env):
    expr = FormatExpression(jinja_globals_env, '{{ mailto_link("joe@example.com", "Joseph") }}')
    assert expr.evaluate() == '<a href="mailto:joe@example.com">Joseph</a>'
