'''A concrete apport.PackageInfo class implementation for Fedora.

Copyright (C) 2007 Red Hat Inc.
Author: Will Woods <wwoods@redhat.com>

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
the full text of the license.
'''

from packaging_rpm import RPMPackageInfo
from rpmUtils.miscutils import compareEVR, stringToVersion

class __FedoraPackageInfo(RPMPackageInfo):
    '''Concrete apport.PackageInfo class implementation for Fedora.'''

    # A list of ids of official keys used by the Fedora project
    official_keylist = ('30c9ecf8','4f2a6fd2','897da07a','1ac70ce6')

    def __distro_is_rawhide(self):
        '''Check to see if we're running rawhide, so we know that it's OK if
        a package is unsigned.'''
        f = open("/etc/fedora-release")
        line = f.readline()
        f.close()
        if "Rawhide" in line:
            return True
        else:
            return False

    def is_distro_package(self, package):
        '''Check if a package is a genuine distro package (True) or comes from
        a third-party source.'''
        if RPMPackageInfo.is_distro_package(self,package):
            # GPG key id checks out OK. Yay!
            return True
        else:
            # GPG key check failed.
            # In Fedora, rawhide packages aren't signed - even official ones.
            # So check to see if we're running rawhide, and if so, fall back
            # to something stupid, like checking for "Red Hat" in distribution
            # and vendor tags.

            # NOTE the superclass method also does _get_header and then
            # throws it away. This is somewhat wasteful.
            hdr = RPMPackageInfo._get_header(self,package)

            if self.__distro_is_rawhide() and \
               hdr['vendor'] == "Red Hat, Inc." and \
               hdr['distribution'].startswith("Red Hat"):
                return True
        return False

    def get_available_version(self, package):
        '''Return the latest available version of a package.'''
        # used in report.py, which is used by the frontends
        (epoch, name, ver, rel, arch) = self._split_envra(package)
        package_ver = '%s-%s' % (ver,rel)
        if epoch: 
            package_ver = "%s:%s" % (epoch, package_ver)
        # FIXME STUB
        return package_ver

    def get_source_tree(self, srcpackage, dir, version=None):
        '''Download given source package and unpack it into dir (which should
        be empty).

        This also has to care about applying patches etc., so that dir will
        eventually contain the actually compiled source.

        If version is given, this particular version will be retrieved.
        Otherwise this will fetch the latest available version.

        Return the directory that contains the actual source root directory
        (which might be a subdirectory of dir). Return None if the source is
        not available.'''
        # Used only by apport-retrace.
        # FIXME STUB
        return None

    def compare_versions(self, ver1, ver2):
        '''Compare two package versions.

        Return -1 for ver < ver2, 0 for ver1 == ver2, and 1 for ver1 > ver2.'''
        # Used by crashdb.py (i.e. the frontends)
        return compareEVR(stringToVersion(ver1),stringToVersion(ver2))
        
    def get_file_package(self, file):
        '''Return the package a file belongs to, or None if the file is not
        shipped by any package.
        
        Under normal use, the 'file' argument will always be the executable
        that crashed.
        '''
        # In debian-land, the name of the package is unique enough to identify
        # it, but here in RPMville we have multilib. So we need to identify
        # packages by ENVRA to guarantee uniqueness.
        # Here's the sad part - one quirk of our multilib implementation is
        # that a file can belong to multiple packages. So which one do we
        # choose? If we had context from the crash dump we might know which
        # arch was the important one, but for now.. let's just use the system
        # arch.
        # TODO: provide extra context info (arch?) from the crash dump
        hdrs = self._get_headers_by_tag('basenames',file)
        h = None
        if len(hdrs) > 1: # Multiple files own this package - multiarch!
            for h in hdrs:
                if h['arch'] == self.get_system_architecture():
                    break
        else:
            h = hdrs[0]
        return self._make_envra_from_header(h)          

impl = __FedoraPackageInfo()
