import setuptools, platform

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    REQUIRES = fr.read()

setuptools.setup(
    name="ble-serial",
    version="2.2.0",
    author="Jake",
    author_email="ble-serial-pypi@ja-ke.tech",
    description="A package to connect BLE serial adapters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jakeler/ble-serial",
    packages=[
        "ble_serial",
        "ble_serial.bluetooth",
        "ble_serial.ports",
        "ble_serial.scan",
        "ble_serial.setup_com0com",
        "ble_serial.log",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=REQUIRES,
    entry_points={
        'console_scripts': [
            'ble-scan=ble_serial.scan:main',
            'ble-serial=ble_serial.main:launch',
        ] + (
            ['ble-com-setup=ble_serial.setup_com0com:main'] if platform.system() == "Windows"
            else []
        )
    },
)
