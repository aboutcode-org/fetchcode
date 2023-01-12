import gzip
import os

import debian_inspector
import requests
from debian_inspector import copyright as debcopy, debcon
from extractcode.api import extract_archives
from packageurl import PackageURL

from fetchcode import ls, fetch
from fetchcode.packagedcode_models import Party, DependentPackage


def get_response(url):
    """
    Generate `Package` object for a `url` string
    """
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()

    raise Exception(f"Failed to fetch: {url}")


def get_pypi_bugtracker_url(project_urls):
    bug_tracking_url = project_urls.get("Tracker")
    if not bug_tracking_url:
        bug_tracking_url = project_urls.get("Issue Tracker")
    if not bug_tracking_url:
        bug_tracking_url = project_urls.get("Bug Tracker")
    return bug_tracking_url


def get_pypi_codeview_url(project_urls):
    code_view_url = project_urls.get("Source")
    if not code_view_url:
        code_view_url = project_urls.get("Code")
    if not code_view_url:
        code_view_url = project_urls.get("Source Code")
    return code_view_url


def extract_gzip_data(file_loc):
    with gzip.open(file_loc, "r") as file:
        content = file.read().decode("utf-8")
    return content


def parse_license(location):
    """
    Return a list of License paragraphs from Debian copyright file at location.
    """
    copyparas = debcopy.DebianCopyright.from_file(location)
    return [
        para
        for para in copyparas.paragraphs
        if isinstance(para, debian_inspector.copyright.CopyrightLicenseParagraph)
    ]


def get_vcs_repo(description):
    """
    Return a tuple of (vcs_tool, vcs_repo) or (None, None) if no vcs_repo is found.
    """
    repos = []
    for vcs_tool, vcs_repo in description.items():
        vcs_tool = vcs_tool.lower()
        if not vcs_tool.startswith("vcs-") or vcs_tool.startswith("vcs-browser"):
            continue
        _, _, vcs_tool = vcs_tool.partition("-")
        repos.append((vcs_tool, vcs_repo))

    if len(repos) > 1:
        raise TypeError(
            "Debian description with more than one Vcs repos: %(repos)r" % locals()
        )

    if repos:
        vcs_tool, vcs_repo = repos[0]
    else:
        vcs_tool = None
        vcs_repo = None

    return vcs_tool, vcs_repo


# TODO: Fix this function in minecode
def parse_email(text):
    """
    From minecode
    Return a tuple of (name, email) extracted from a `text` string.
        Debian TeX Maintainers <debian-tex-maint@lists.debian.org>
    """
    if not text:
        return None, None
    name, _, email = text.partition("<")
    name = name.strip()
    email = email.strip()
    if not email:
        return name, email
    email = email.strip(">")
    return name, email


def get_dependencies(data):
    """
    From minecode
    Return a list of DependentPackage extracted from a Debian `data` mapping.
    """
    scopes = {
        "build-depends": dict(is_runtime=False, is_optional=True),
        "depends": dict(is_runtime=True, is_optional=False),
        "pre-depends": dict(is_runtime=True, is_optional=False),
        # 'Provides': dict(is_runtime=True, is_optional=False),
        # 'Recommends': dict(is_runtime=True, is_optional=True),
        # 'Suggests': dict(is_runtime=True, is_optional=True),
    }
    dep_pkgs = []
    for scope, flags in scopes.items():
        depends = data.get(scope)
        if not depends:
            continue

        dependencies = comma_separated(depends)
        name_version = []
        for dependency in dependencies:
            version_constraint = None
            if "(" in dependency and ")" in dependency:
                start = dependency.index("(")
                end = dependency.index(")")
                version_constraint = dependency[start + 1 : end]
            name = dependency.split(" ")[0]
            name_version.append([name, version_constraint])

        # break each dep in package names and version constraints
        # FIXME:!!!
        # FIXED !!!
        for name, version_constraint in name_version:
            purl = PackageURL(type="deb", namespace="debian", name=name)
            dep = DependentPackage(
                purl=purl.to_string(),
                scope=scope,
                requirement=version_constraint,
                **flags,
            )
            dep_pkgs.append(dep)

    return dep_pkgs


def comma_separated(text):
    """
    Return a list of strings from a comma-separated text.
    """
    if not text:
        return []
    return [t.strip() for t in text.split(",") if t and t.strip()]


# TODO: Document All changes for god's sake, don't forget it >.<
def process_debian_data(package_name, source):
    """
    :parameter `package_name` Takes package name [with file_extension].
    :parameter `source` a bool True if given package is a source package (.debian.tar.gz) or a binary package(.deb).
    :returns a dictionary with keys (licenses, vcs_url, homepage_url, description, size, release_date, download_url)
    """

    base_path = f"https://ftp.debian.org/debian"

    # Fetching ls-lR.gz file.
    index_file_response = fetch(f"{base_path}/ls-lR.gz")
    if not index_file_response.success:
        return Exception(f"Unable to fetch {base_path}/ls-lR.gz")

    index_content = extract_gzip_data(index_file_response.location)
    entries = ls.parse_directory_listing(index_content)

    package_entry = None

    for entry in entries:
        if entry.type == ls.FILE:
            if entry.path.startswith("pool/main") and entry.path.endswith(package_name):
                package_entry = entry
            if package_entry is not None:
                break

    if package_entry is None:
        raise Exception(f"Unable to find {package_name} in Debian Pool")

    # Fetching the actual package
    package_pool_location = f"{base_path}/{package_entry.path}"
    package_response = fetch(package_pool_location)
    if not package_response.success:
        raise Exception(f"Unable to fetch {package_pool_location}")

    # Extracting the package using extractcode
    for _ in extract_archives(package_response.location):
        pass

    extracted_package_location = f"{package_response.location}-extract"

    # If the requested package is a source file [.debian.tar.gz]
    if source:
        copyright_location = f"{extracted_package_location}/debian/copyright"
        control_location = f"{extracted_package_location}/debian/control"

    # If the requested package is a binary Package
    else:
        control_folder = "control.tar.gz-extract"
        for folder in os.listdir(extracted_package_location):
            if folder.startswith("control") and folder.endswith("extract"):
                control_folder = folder
                break
        copyright_location = f"{extracted_package_location}/data.tar.xz-extract/usr/share/doc/{package_name.split('_')[0]}/copyright"
        control_location = f"{extracted_package_location}/{control_folder}/control"

    # Getting Licenses
    licenses = []
    for CopyrightLicenseParagraph in parse_license(copyright_location):
        licenses.append(CopyrightLicenseParagraph.license.name)

    with open(control_location, "r") as control_file:
        control_file_data = control_file.read()

    control_file_content = debcon.Debian822.from_string(control_file_data).to_dict()

    # Getting vcs_info
    tool, vcs_url = get_vcs_repo(control_file_content)

    # Getting HomepageURL
    homepage_url = control_file_content.get("homepage")

    # Getting Description
    description = control_file_content.get("description")

    # Getting Size
    size = package_entry.size

    # Getting release_date
    release_date = package_entry.date

    # Getting Maintainers and Uploaders
    parties = []
    maintainer_names = comma_separated(control_file_content.get("maintainer", ""))
    if maintainer_names:
        for maintainer in maintainer_names:
            name, email = parse_email(maintainer)
            if name:
                party = Party(name=name, role="maintainer", email=email)
                parties.append(party)
    contributor_names = comma_separated(control_file_content.get("uploaders", ""))
    if contributor_names:
        for contributor in contributor_names:
            name, email = parse_email(contributor)
            if name:
                party = Party(name=name, role="contributor", email=email)
                parties.append(party)

    # Getting Dependencies
    dependencies = get_dependencies(control_file_content)

    return dict(
        declared_license=" ,".join(licenses),
        vcs_url=vcs_url,
        homepage_url=homepage_url,
        description=description,
        size=size,
        release_date=release_date,
        download_url=package_pool_location,
        dependencies=dependencies,
        parties=parties,
    )
