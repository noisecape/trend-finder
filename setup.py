from setuptools import setup, find_packages

setup(
    name='trend_finder',                     # Replace with your package name
    version='0.1.0',
    packages=find_packages(),             # Automatically find all packages and subpackages
    install_requires=[                    # List any dependencies your package needs
        # e.g., 'numpy', 'requests'
    ],
    author='Tommaso Capecchi',
    description='Just a trend-finder based on Reddit data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/noisecape/trend-finder',  # Replace with your repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12.4',             # Specify the Python versions you support
)