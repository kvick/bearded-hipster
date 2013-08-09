#!/usr/bin/env python
#
# Detect when a resolved dependancy is older than the currently available
# released version.  Parses the ivy transitive-dependencies.txt file and
# asks Scruffy for the versions available for each
#
# Step 1. for each dependancy find the distance from the latest release version
# Step 2. look for multiple versions of the same dep (e.g. base-server-explorer)
#

import logging
import re
import optparse
import requests

from bs4 import BeautifulSoup
import requests

# http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
def versiontuple(v):
    return tuple(map(int, (v.split("."))))

def get_for_lib(log, org, lib, version):
    """docstring for get_for_lib"""

    module_url = '{0}/{1}'.format(org, lib)
    log.debug(' - checking {0} for version {1}'.format(module_url, version))
    all_versions = get_versions_from_scruffy(log, module_url)
    newer_release_versions = get_newer_versions(log, all_versions['release'], version)
    newer_candidate_versions = get_newer_versions(log, all_versions['candidate'], version)
    newer_snapshot_versions = get_newer_versions(log, all_versions['snapshot'], version)

    # I'm embarrassed by this code.  try to find out what release level we're in
    found_release = None
    release = None

    if newer_release_versions is not None: 
        found_release = newer_release_versions
        release = 'release'

    if newer_candidate_versions is not None:
        found_release = newer_candidate_versions
        release = 'candidate'

    if newer_snapshot_versions is not None:
        found_release = newer_snapshot_versions
        release = 'snapshot'

    if found_release is None:
        log.error('unable to find {0} in ANY of the release/snapshot/candidate. \
                   this shouldn\'t happen'.format(version))
        return

    newer_count = len(found_release)
    if newer_count > 0:
        log.info(' * {0}/{1}/{2} from {3} is BEHIND'.format(org, lib, version,
                                                            release.upper()))
        log.info('   ! there are {0} newer version(s) available in {1}'.format(newer_count, 
                                                                           release))
        log.debug('    ! -> {0}'.format(found_release))
    else:
        log.info(' = {0}/{1}/{2} from {3} is OK'.format(org, lib, version,
                                                            release.upper()))


def parse_file(log, filename):
    """"""
    with open(filename, 'r') as dep_file:
       for line in dep_file:
           if line:
               match = re.search('^([\w\d.]+)#([\w\d-]+);([\d\w.-]+)', line)
               if match:
                   log.debug('org={0}, lib={1}, version={2}'.format(match.group(1),
                                                                match.group(2),
                                                                match.group(3)))
                   get_for_lib(log, match.group(1),match.group(2),match.group(3))

def get_versions_from_scruffy(log, module_url):
    """return an dict containing an arrays for each release level containing the
    versions for the module 
    e.g. {'release' : ['1.0', '2.0']} 
    """

    url = 'http://scruffy.netflix.com/modules/%s'

    r = requests.get(url % module_url)
    soup = BeautifulSoup(r.text)
    
    releases = ['release', 'candidate', 'snapshot']
    scruffy_prefix = 'rev '   # add this to find the right css class (e.g. 'rev release')
    all_versions = {}

    # find by the CSS 'rev X' class
    for release in releases:
        log.debug(' - checking scruffy for {0} in the {1}'.format(module_url,
                                                              scruffy_prefix +
                                                              release))

        versions = []
        for revision in soup.find_all("a", class_=scruffy_prefix + release):
            versions.append(revision.contents[0])

        all_versions[release] = versions

        log.debug(' =========== {0} versions ========== '.format(release)) 
        log.debug(versions)

    return all_versions

def get_newer_versions(log, module_versions, version):
    """given a list of ordered versions if the version is in this list
       print how far away the given version is from latest (last) element"""
    
    log.debug("looking for %s" % version)

    length = len(module_versions)
    if not version in module_versions:
        log.debug(module_versions)
        return None
    else:
        index = module_versions.index(version)
        log.debug('{0} found at position {1} of {2}'.format(version, index + 1, length))
        newer_versions = module_versions[index - length:]
        newer_versions.remove(version)

        if len(newer_versions) > 0:
            log.debug('newer versions = {0}'.format(newer_versions)) 
        else:
            log.debug('up-to-date')

        return newer_versions

def main():
    logging.basicConfig(filename='dep.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
 
    # supress requests log messages
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING) 

    log = logging.getLogger(__name__)
    p = optparse.OptionParser()
    p.add_option('--file', '-f', default="transitive-dependencies.txt")
    options, arguments = p.parse_args()

    logging.info('Started. parsing {0}'.format(options.file))
    parse_file(log, options.file)

    # Testing
    #release_versions = get_versions_from_scruffy(log, 'netflix/astyanax')
    #get_newer_versions(log, release_versions, '1.34.0')

    #get_newer_versions(log, [u'1.34.0'], '1.34.0')
    #get_newer_versions(log, [u'1.33.0', u'1.34.0', u'1.35.0'], '1.34.0')
    #get_newer_versions(log, [u'1.34.0', u'1.35.0'], '1.39.0')

    log.info("Finished")

if __name__ == '__main__':
    main()
