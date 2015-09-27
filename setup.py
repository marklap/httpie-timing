from setuptools import setup
from httpie_timing import VERSION

setup(
    name='httpie-timing',
    description='Plugin to add timing statements to the output of HTTPie.',
    long_description=open('README.md').read().strip(),
    version=VERSION,
    author='Mark LaPerriere',
    author_email='marklap@gmail.com',
    license='MIT',
    url='https://github.com/marklap/httpie-timing',
    download_url='https://github.com/marklap/httpie-timing',
    py_modules=['httpie_timing'],
    zip_safe=False,
    entry_points={
        'httpie.plugins.transport.v1': [
            'httpie_timing_http = httpie_timing:TimingHTTPPlugin',
            'httpie_timing_https = httpie_timing:TimingHTTPSPlugin'
        ],
        'httpie.plugins.formatter.v1': [
            'httpie_timing_formatter = httpie_timing:TimingFormatterPlugin',
        ]
    },
    install_requires=[
        'httpie>=0.9.2',
        'requests>=2.7.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Environment :: Plugins',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
    ],
)
