# /// script
# dependencies = ["nox", "nox_uv"]
# ///
import nox
import nox_uv

# by default, only build
nox.options.sessions = ["build"]
nox.options.stop_on_first_error = True
nox.options.default_venv_backend = "uv"


@nox_uv.session
def build(s: nox.Session) -> None:
    """Build the HTML for the getlektor.com website."""
    s.run("lektor", "build", "-f", "webpack", "-O", "_html")


@nox.session(requires=["build"], python=False, tags=["tests"])
def htmltest(s: nox.Session) -> None:
    """Check generated HTML.

    Requires that `htmltest`_ be installed and on $PATH.

    .. _htmltest: https://github.com/wjdp/htmltest
    """
    s.run("htmltest", "-c", ".htmltest.yml", "-s", "_html", external=True)


if __name__ == "__main__":
    nox.main()
