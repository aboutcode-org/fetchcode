FetchCode: Utilities to fetch code from purls, URLs and version control repos.
================================================================================

FetchCode is a library to reliably fetch code via HTTP, FTP and version control
systems. It can work using plain HTTP and FTP URLs, as well as
`Package URLs <https://github.com/package-url>`_ and version control (VCS) URLs
as used in Python pip and as specified in `SPDX Package Download Location
<https://spdx.github.io/spdx-spec/3-package-information/#37-package-download-location>`_

Homepage and support: https://github.com/aboutcode-org/fetchcode


Why FetchCode?
--------------

It is surprisingly difficult to have a simple API to consistently fetch code
from package repositories, version control repositories and APIs: each site
and each package manager has its own unique and peculiar ways. FetchCode goal
is to abstract all these details and make it easy to fetch things reliably.


Development installation
--------------------------

Clone the repo::

    git clone https://github.com/aboutcode-org/fetchcode

Then install all the requirements using this command (on POSIX)::

    ./configure --dev


Running tests
----------------

To run test suite use::

    pytest -vvs


Usage
--------

Fetch a code archive and get a ``fetchcode.fetch.Response`` object back::

    >>> from fetchcode import fetch
    >>> f = fetch('https://github.com/aboutcode-org/fetchcode/archive/ab65b2e645c889887227ea49eb3332d885fd0a54.zip')
    >>> f.location
    '/tmp/tmp_cm02xsg'
    >>> f.content_type
    'application/zip'
    >>> f.url
    'https://github.com/aboutcode-org/fetchcode/archive/ab65b2e645c889887227ea49eb3332d885fd0a54.zip'

Fetch some package metadata and get a ``fetchcode.packagedcode_models.Package`` object back::

    >>> from fetchcode import package
    >>> list(package.info('pkg:rubygems/files'))
    [Package(type='rubygems', namespace=None, name='files', version=None)]


License
--------

- SPDX-License-Identifier: Apache-2.0

Copyright (c) nexB Inc. and others.


Acknowledgements, Funding, Support and Sponsoring
--------------------------------------------------------

This project is funded, supported and sponsored by:

- Generous support and contributions from users like you!
- the European Commission NGI programme
- the NLnet Foundation 
- the Swiss State Secretariat for Education, Research and Innovation (SERI)
- Google, including the Google Summer of Code and the Google Seasons of Doc programmes
- Mercedes-Benz Group
- Microsoft and Microsoft Azure
- AboutCode ASBL
- nexB Inc. 



|europa|   |dgconnect| 

|ngi|   |nlnet|   

|aboutcode|  |nexb|


This project was funded through the NGI0 Core Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101092990.

|ngizerocore| https://nlnet.nl/project/VulnerableCode-enhancements/


This project was funded through the NGI0 Entrust Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101069594. 

|ngizeroentrust| https://nlnet.nl/project/Back2source/


This project was funded through the NGI0 Core Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101092990.

|ngizerocore| https://nlnet.nl/project/Back2source-next/


This project was funded through the NGI0 Entrust Fund, a fund established by NLnet with financial
support from the European Commission's Next Generation Internet programme, under the aegis of DG
Communications Networks, Content and Technology under grant agreement No 101069594. 

|ngizeroentrust| https://nlnet.nl/project/purl2all/



.. |nlnet| image:: https://nlnet.nl/logo/banner.png
    :target: https://nlnet.nl
    :height: 50
    :alt: NLnet foundation logo

.. |ngi| image:: https://ngi.eu/wp-content/uploads/thegem-logos/logo_8269bc6efcf731d34b6385775d76511d_1x.png
    :target: https://ngi.eu35
    :height: 50
    :alt: NGI logo

.. |nexb| image:: https://nexb.com/wp-content/uploads/2022/04/nexB.svg
    :target: https://nexb.com
    :height: 30
    :alt: nexB logo

.. |europa| image:: https://ngi.eu/wp-content/uploads/sites/77/2017/10/bandiera_stelle.png
    :target: http://ec.europa.eu/index_en.htm
    :height: 40
    :alt: Europa logo

.. |aboutcode| image:: https://aboutcode.org/wp-content/uploads/2023/10/AboutCode.svg
    :target: https://aboutcode.org/
    :height: 30
    :alt: AboutCode logo

.. |swiss| image:: https://www.sbfi.admin.ch/sbfi/en/_jcr_content/logo/image.imagespooler.png/1493119032540/logo.png
    :target: https://www.sbfi.admin.ch/sbfi/en/home/seri/seri.html
    :height: 40
    :alt: Swiss logo

.. |dgconnect| image:: https://commission.europa.eu/themes/contrib/oe_theme/dist/ec/images/logo/positive/logo-ec--en.svg
    :target: https://commission.europa.eu/about-european-commission/departments-and-executive-agencies/communications-networks-content-and-technology_en
    :height: 40
    :alt: EC DG Connect logo

.. |ngizerocore| image:: https://nlnet.nl/image/logos/NGI0_tag.svg
    :target: https://nlnet.nl/core
    :height: 40
    :alt: NGI Zero Core Logo

.. |ngizerocommons| image:: https://nlnet.nl/image/logos/NGI0_tag.svg
    :target: https://nlnet.nl/commonsfund/
    :height: 40
    :alt: NGI Zero Commons Logo

.. |ngizeropet| image:: https://nlnet.nl/image/logos/NGI0PET_tag.svg
    :target: https://nlnet.nl/PET
    :height: 40
    :alt: NGI Zero PET logo

.. |ngizeroentrust| image:: https://nlnet.nl/image/logos/NGI0Entrust_tag.svg
    :target: https://nlnet.nl/entrust
    :height: 38
    :alt: NGI Zero Entrust logo

.. |ngiassure| image:: https://nlnet.nl/image/logos/NGIAssure_tag.svg
    :target: https://nlnet.nl/image/logos/NGIAssure_tag.svg
    :height: 32
    :alt: NGI Assure logo

.. |ngidiscovery| image:: https://nlnet.nl/image/logos/NGI0Discovery_tag.svg
    :target: https://nlnet.nl/discovery/
    :height: 40
    :alt: NGI Discovery logo









