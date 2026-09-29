from setuptools import find_packages, setup


setup(
    name="vehicle-speed-checker",
    version="0.1.0",
    description="Vehicle speed compliance checker for GitHub Copilot training",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.9",
    install_requires=["Flask>=3.0,<4.0"],
    extras_require={"test": ["pytest>=8.0,<9.0"]},
)