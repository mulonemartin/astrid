
""" ``config`` module.
"""

from astrid.routing.builders import try_build_plain_route
from astrid.routing.builders import try_build_curly_route
from astrid.routing.builders import try_build_regex_route

from astrid.routing.curly import patterns as curly_patterns
from astrid.routing.curly import default_pattern as curly_default_pattern

route_builders = [
    try_build_plain_route,
    try_build_curly_route,
    try_build_regex_route
]
