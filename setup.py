from setuptools import setup, find_packages
setup(
    name="yaixm",
    version="1.4.2",
    description="YAML/JSON simplified AIXM",
    url="https://gitlab.com/ahsparrow/yaixm",
    author="Alan Sparrow",
    author_email="yaixm@freeflight.org.uk",
    license="GPL",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    keywords=['airspace', 'aixm', 'openair'],
    install_requires=["jsonschema", "PyYAML", "strict-rfc3339"],
    packages=find_packages(),
    package_data={
        'yaixm': ["data/schema.yaml"]
    },
    entry_points={
        'console_scripts': [
            "yaixm_check = yaixm.cli:check",
            "yaixm_openair = yaixm.cli:openair",
            "yaixm_tnp = yaixm.cli:tnp",
            "yaixm_json = yaixm.cli:to_json",
            "yaixm_merge = yaixm.cli:merge",
            "yaixm_geojson = yaixm.cli:geojson"
        ]
    }
)
