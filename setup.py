from setuptools import find_packages, setup
setup(
    name="tdpcda",
    packages=find_packages(include=['tdpcda']),
    version="0.0.1",
    description="TDP CDA Testing Library",
    install_requires=['requests', 'uuid'],
    author="Todd Pihl",
    license="Apache 2.0",
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests'
)