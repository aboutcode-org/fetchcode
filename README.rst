*********
Fetchcode
*********
It is a library to reliably fetch code via HTTP, FTP and version control systems. 

Installation
############
Clone the repo using 
`git clone https://github.com/nexB/fetchcode`

Then install all the requirements using 
`pip3 install -r requirements.txt`

Running test suite
##################

To run test suite
`python3 -m pytest`

Usage of API to fetch HTTP/S and FTP URLs
#########################################

.. code-block:: python

    from fetchcode import fetch
    url = 'A Http or FTP URL'
    # This returns a response object which has attributes
    # 'content_type' content type of the file
    # 'location' the absolute location of the files that was fetched
    # 'scheme' scheme of the URL
    # 'size' size of the retrieved content in bytes
    # 'url' fetched URL
    resp = fetch(url = url)