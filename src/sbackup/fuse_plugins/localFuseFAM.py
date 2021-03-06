#   Simple Backup - local fuse plugin 
#
#   Copyright (c)2009-2010: Jean-Peer Lorenz <peer.loz@gmx.net>
#   Copyright (c)2007-2008: Ouattara Oumar Aziz <wattazoum@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from sbackup.fuse_plugins import pluginFAM
from sbackup.util import local_file_utils


class localFuseFAM (pluginFAM):
    """
    The localFuseFAM plugin do nothing when the mount method is called
    @author: Oumar Aziz Ouattara <wattazoum@gmail.com>
    @version: 1.0
    """
    def __init__(self):
        pluginFAM.__init__(self)

    def match_scheme(self, remoteSource):
        return remoteSource.startswith(local_file_utils.PATHSEP)

    def match_scheme_full(self, remoteSource):
        """
        Try to match the scheme of the remoteSource.
        @param remoteSource: The remote path
        @return: True if the scheme matches the one for this 
        @rtype: boolean
        """
        return remoteSource.startswith(local_file_utils.PATHSEP)

    def mount(self, source, mountbase):
        """
        Fake mounter to be used by the fuseFAM
        @param source: The remote path
        @param mountbase: The mount points base dir
        @return: The mount point complete path
        @rtype: str
        """
        self.logger.debug("Nothing to do for '%s'" % source)
        return (local_file_utils.PATHSEP, "", source.lstrip(local_file_utils.PATHSEP))

    def umount(self, mounteddir):
        """
        """
        self.logger.debug("No need to unmount %s" % mounteddir)
