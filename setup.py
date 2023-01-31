from setuptools import setup

setup(
    name='pybuild',
    version='0.1.0',
    description='A module to bind Fortran with Python',
    author='Guillaume Roullet',
    author_email='roullet@univ-brest.fr',
    license='MIT License',
    packages=['pybuild'],
    install_requires=['mpi4py>=2.0',
                      'numpy',
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
