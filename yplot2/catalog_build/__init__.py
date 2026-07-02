"""
Catalog build tooling for yplot2.

This subpackage contains the catalog build orchestrator and supporting
modules. It is separate from ``yplot2.catalog`` (the @catalog decorator).

Importing this package pulls in matplotlib (for fingerprint) but NOT
seaborn or pandas. Use ``from yplot2.catalog_build import build_catalog``
to trigger the full build, or run the CLI directly::

    python -m yplot2.catalog_build.build --out-dir catalog

Exports:
    build_catalog: Main entry point; collects + fingerprints + writes output.
    BuildReport: Dataclass summarising a build run.
"""

__all__ = ["build_catalog", "BuildReport"]


def __getattr__(name: str) -> object:
    """Lazy-load build_catalog and BuildReport on first access (PEP 562).

    Avoids the RuntimeWarning that occurs when Python runs
    ``python -m yplot2.catalog_build.build`` and finds the module already
    in sys.modules due to the package __init__ having imported it eagerly.

    Args:
        name: Attribute name to resolve.

    Returns:
        The requested attribute.

    Raises:
        AttributeError: When *name* is not a known export.
    """
    if name == "build_catalog":
        from .build import build_catalog  # type: ignore[import]

        return build_catalog
    if name == "BuildReport":
        from .build import BuildReport  # type: ignore[import]

        return BuildReport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
