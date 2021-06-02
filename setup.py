import setuptools, platform

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    REQUIRES = fr.read()

setuptools.setup(
    name="ble-serial",
    version="2.2.1",
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
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Communications",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
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
