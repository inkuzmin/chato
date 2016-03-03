from setuptools import setup, find_packages

setup(
    name="chato",
    version='0.1',
    description="A Chat Server and Client that tries not to be so annoying",
    author="Nicholas Amorim",
    author_email="nicholas@alienretro.com",
    url="https://github.com/nicholasamorim/chato",
    license="GPL",
    packages=find_packages(),
    install_requires=['crossbar', 'cassandra-driver'],
    tests_require=['mock', 'tox'],
    keywords='api consumer client chat rest websockets django',
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Topic :: Communications :: Chat",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)