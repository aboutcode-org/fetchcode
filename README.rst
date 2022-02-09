FetchCode: Utilities to fetch code from purls, URLs and version control repos. 
================================================================================

FetchCode is a library to reliably fetch code via HTTP, FTP and version control
systems. It can work using plain HTTP and FTP URLs, as well as 
`Package URLs <https://github.com/package-url>`_ and version control (VCS) URLs
as used in Python pip and as specified in `SPDX Package Download Location
<https://spdx.github.io/spdx-spec/3-package-information/#37-package-download-location>`_

Homepage and support: https://github.com/nexB/fetchcode


Why FetchCode?
--------------

It is surprisingly difficult to have a simple API to consistently fetch code
from package repositories, version control repositories and APIs: each site
and each package manager has its own unique and peculiar ways. FetchCode goal
is to abstract all these details and make it easy to fetch things reliably.


Development installation
--------------------------

Clone the repo::

    git clone https://github.com/nexB/fetchcode

Then install all the requirements using::

    configure --dev


Running tests
----------------

To run test suite use::

    pytest -vvs


Usage
--------

Fetch a code archive and get a ``fetchcode.fetch.Reposnse`` object back::

    >>> from fetchcode import fetch
    >>> f = fetch('https://github.com/nexB/fetchcode/archive/ab65b2e645c889887227ea49eb3332d885fd0a54.zip')
    >>> f.location
    '/tmp/tmp_cm02xsg'
    >>> f.content_type
    'application/zip'
    >>> f.url
    'https://github.com/nexB/fetchcode/archive/ab65b2e645c889887227ea49eb3332d885fd0a54.zip'

Fetch some package metadata and get a ``fetchcode.packagedcode_models.Package`` object back::

    >>> from fetchcode import package
    >>> list(package.info('pkg:rubygems/files'))
    [Package(type='rubygems', namespace=None, name='files', version=None)]


License
--------

- SPDX-License-Identifier: Apache-2.0

Copyright (c) nexB Inc. and others.
