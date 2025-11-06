from setuptools import setup, find_packages

setup(
    name="pet_comparison",
    version="0.1.0",
    description="A comprehensive comparison of different PET (Potential Evapotranspiration) formulas",
    author="licm13",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "xarray>=0.19.0",
        "netCDF4>=1.5.7",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],
    },
    python_requires=">=3.8",
)
