from email.utils import getaddresses
from typing import Optional

from markupsafe import Markup

from lektor.pluginsystem import Plugin


def mailto_link(email_address: str, default_link_text: Optional[str] = None) -> Markup:
    """Format an HTML link to a mailto: URL to ``email_address``.

    ``Email_address`` should be a string containing one or more
    comma-separated RFC5322 addresses.  Any *display-name*\\s included
    in ``email_address`` will be stripped, before use in the
    ``mailto:`` URL.  (RFC6068_ allows only *addr-spec*\\s in the
    ``mailto:`` URI.)

    The link text will be formed from the *display-name*\\s extracted
    from ``email_address``.  If there are none, they the link text
    will be taken from the value of the optional ``display_name``
    parameter.  If that is empty, the link text will be the value of
    ``email_address``.

    Background
    **********

    This filter is useful for massaging a distributions "Author-email"
    and "Author" metadata fields into a valid mailto link. Sometimes
    the author's name gets folded into the "Author-email" field
    (e.g. ``"Author Name <author@example.org>"``), and sometimes it is
    separated out into the "Author" field.

    According to PEP621_, when both author ``name`` and ``email`` are
    specified in ``pyproject.toml``, both of those wind up in the
    "Author-Email" metadata field. In that case, the "Author" metadata
    field remains empty.

    In constrast, historically, (e.g. in ``setup.py`` based projects) it
    seems to have been common practice to put the author's name in
    "Author" and their email in "Author-Email". (Of note, the `Core Metadata
    Spec<mdspec_>`_ is not particularly opinionated on whether the
    author name(s) should go into "Author", "Author-Email", or both.)

    .. _PEP621: https://peps.python.org/pep-0621/#authors-maintainers
    .. _mdspec: https://packaging.python.org/en/latest/specifications/core-metadata/#author
    .. _RFC6068: https://datatracker.ietf.org/doc/html/rfc6068

    """
    addresses = getaddresses([email_address])
    addr_specs = ", ".join(addr_spec for name, addr_spec in addresses if addr_spec)
    if not addr_specs:
        return Markup("")
    
    link_text = ", ".join(name for name, addr_spec in addresses if name)
    if not link_text:
        link_text = default_link_text or addr_specs

    return Markup('<a href="mailto:{addr_specs}">{link_text}</a>').format(**locals())


class JinjaGlobalsPlugin(Plugin):
    name = "Jinja Globals"
    description = "Custom Jinja globals and filters for lektor-website."

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals.update(
            {
                "mailto_link": mailto_link,
            }
        )
