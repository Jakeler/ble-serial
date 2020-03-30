import setuptools

with open("README-pypi.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ble-serial",
    version="1.1.0",
    author="Jake",
    author_email="ble-serial-pypi@ja-ke.tech",
    description="A package to connect BLE serial adapters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jakeler/ble-serial",
    packages=["ble_serial"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'ble-scan=ble_serial.scan:main',
            'ble-serial=ble_serial.__main__:main',
        ]
    },
)
