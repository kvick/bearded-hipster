#!/usr/bin/env python
#
# Step 1. For Netflix libs Detect that I got a version older
# parse transitive-dependencies.txt for library/version
# for each library, ask scruffy how many released versions away the version 
# I have is from what I got.  

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
    log.info('processing {0} for version {1}'.format(module_url, version))
    versions = get_versions_from_scruffy(log, module_url)
    compare_versions(log, versions, version)

def parse_file(log, filename):
    """"""
    with open(filename, 'r') as dep_file:
       for line in dep_file:
           if line:
               match = re.search('^([\w\d.]+)#([\w\d-]+);([\d.-]+)', line)
               if match:
                   log.info('org={0}, lib={1}, version={2}'.format(match.group(1),
                                                                match.group(2),
                                                                match.group(3)))
                   get_for_lib(log, match.group(1),match.group(2),match.group(3))

def get_versions_from_scruffy(log, module_url):
    """docstring for get_versions_from_scruffy"""
    url = 'http://scruffy.netflix.com/modules/%s'

    r = requests.get(url % module_url)
    soup = BeautifulSoup(r.text)
    
    release_versions = []
    # find by the CSS 'rev release' class
    for revision in soup.find_all("a", class_="rev release"):
        release_versions.append(str(revision.contents))

    log.debug(" =========== release versions ========== ") 
    log.debug(release_versions)
    return release_versions

def compare_versions(log, module_versions, version):
    """given a list of ordered versions if the version is in this list
       print how far away the given version is from latest (last) element"""
    
    log.debug("looking for %s" % version)

    length = len(module_versions)
    if not version in module_versions:
        log.info('didn\'t find {0} in {1} versions'.format(version, length))
        log.debug(module_versions)
        return None
    else:
        index = module_versions.index(version)
        log.debug('{0} found at position {1} of {2}'.format(version, index + 1, length))
        newer_versions = module_versions[index - length:]
        newer_versions.remove(version)
        if len(newer_versions) > 0:
            log.debug('newer versions = {0}'.format(newer_versions)) 
        newer_count = len(newer_versions)
        log.info('there are {0} newer version(s) available'.format(newer_count))
        return newer_versions

def main():
    logging.basicConfig(filename='dep.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
 
    log = logging.getLogger(__name__)
    logging.info('Started')
    p = optparse.OptionParser()
    p.add_option('--file', '-f', default="transitive-dependencies.txt")
    options, arguments = p.parse_args()

    parse_file(log, options.file)
    #release_versions = get_versions_from_scruffy(log, 'netflix/astyanax')
    #compare_versions(log, release_versions, '1.34.0')

    #compare_versions(log, [u'1.34.0'], '1.34.0')
    #compare_versions(log, [u'1.33.0', u'1.34.0', u'1.35.0'], '1.34.0')
    #compare_versions(log, [u'1.34.0', u'1.35.0'], '1.39.0')

    log.info("Finished")

if __name__ == '__main__':
    main()
