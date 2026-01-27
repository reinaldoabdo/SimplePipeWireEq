from setuptools import setup, find_packages

setup(
    name="simplepipewireq",
    version="1.0.0",
    description="Minimalist 10-band parametric equalizer for PipeWire",
    author="Agent",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "simplepipewireq=simplepipewireq.main:main",
        ],
    },
    install_requires=[
        "gtk4>=4.10.0",
        "PyGObject>=3.46.0",
        "libadwaita>=1.3.0",
    ],
    python_requires=">=3.10",
)
