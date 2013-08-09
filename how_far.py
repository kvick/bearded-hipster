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

def parse_file2(log, filename):
    """"""
    with open(filename, 'r') as dep_file:
       for line in dep_file:
           if line:
               match = re.search('^([\w\d.]+)#([\w\d-]+);([\d.-]+)', line)
               if match:
                   print 'org={0}, lib={1}, version={2}'.format(match.group(1),
                                                                match.group(2),
                                                                match.group(3))

def parse_file(log, filename):
    """ tried to speed things up by using a compiled pattern, doesn't work :( """
    with open(filename, 'r') as dep_file:
       regex = re.compile("(?P<org>^([\w\d.]+)*?)#(?P<lib>([\w\d-]+)*?);(?P<version>([\d.-]+))$")
       for line in dep_file:
           if line:
               stripped_line = line.strip()
               print 'processing line = [{0}]'.format(stripped_line)
               matches = regex.search(stripped_line)

               if matches:
                   results = matches.groupdict()
                   print 'org={0}, lib={1}, version={2}'.format(results['org'],
                                                                results['lib'],
                                                                results['version'])
               else:
                   log.debug('no match found in [{0}]'.format(line))

def get_versions_from_scruffy(log, module_url):
    """docstring for get_versions_from_scruffy"""
    url = 'http://scruffy.netflix.com/modules/%s'

    r = requests.get(url % module_url)
    soup = BeautifulSoup(r.text)
    
    release_versions = []
    for revision in soup.find_all("a", class_="rev release"):
        release_versions.append(revision.contents)

    print release_versions

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

    parse_file2(log, options.file)

    get_versions_from_scruffy(log, 'netflix/astyanax')
    log.info("finished")

if __name__ == '__main__':
    main()
