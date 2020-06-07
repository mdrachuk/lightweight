from setuptools import setup, find_packages

import lightweight


def readme():
    with open('README.md', 'r', encoding='utf8') as f:
        return f.read()


setup(
    name='lightweight',
    version=lightweight.__version__,
    packages=find_packages(exclude=('tests*',)),
    package_data={'lightweight': ['py.typed', 'project-template/**/**/*', 'project-template/**/*', 'project-template/*']},
    entry_points={
        'console_scripts': [
            'lw = lightweight.lw:main',
        ],
    },
    zip_safe=False,
    author='mdrachuk',
    author_email='misha@drach.uk',
    description='Code over configuration static site generator.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/mdrachuk/lightweight',
    license='MIT',
    keywords="static-site-generator",
    python_requires=">=3.7",
    project_urls={
        'Pipelines': 'https://dev.azure.com/misha-drachuk/lightweight',
        'Source': 'https://github.com/mdrachuk/lightweight/',
        'Issues': 'https://github.com/mdrachuk/lightweight/issues',
    },
    install_requires=[
        'Jinja2~=2.11',
        'libsass~=0.19.2',
        'python-frontmatter~=0.4.5',
        'python-slugify~=3.0.3',
        'mistune~=0.8.4',
        'watchgod~=0.5.0',
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Typing :: Typed",
    ],
)
