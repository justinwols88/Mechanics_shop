try:
    from setuptools import setup, find_packages  # type: ignore
except ImportError as e:
    raise SystemExit(
        "setuptools is required to build/install this package. "
        "Install it with: python -m pip install --upgrade pip setuptools"
    ) from e

setup(
    name="mechanics-shop-api",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
)
