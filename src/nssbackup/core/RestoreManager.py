#    NSsbackup - handling of restoration processes
#
#   Copyright (c)2010: Jean-Peer Lorenz <peer.loz@gmx.net>
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

from gettext import gettext as _
import tempfile
import datetime


from nssbackup.core import SnapshotManager
from nssbackup.fs_backend import fam

from nssbackup.util import exceptions
from nssbackup.util import log
from nssbackup.ar_backend import tar


class RestoreManager(object):
    """
    """

    def __init__(self):
        """
        """
        self.logger = log.LogFactory.getLogger()
        self._fop = fam.get_file_operations_facade_instance()

    def restore(self, snapshot, _file):
        """
        Restore one file or directory from the backup tdir with name
        file to its old location.
        All existing files must be moved to a "*.before_restore_$time" files.
        @param snapshot: 
        @param file : 
        """
        self.restoreAs(snapshot = snapshot, _file = _file, target = None)

    def restoreAs(self, snapshot, _file, target, backupFlag = True, failOnNotFound = True) :
        """
        Restore one file or directory from the backup tdir with name
        file to target (or to its old location if None if given to target).
        All existing files must be moved to a "*.before_restore_$time" files.
        @param snapshot:
        @param file :  
        @param target: 
        @param backupFlag: Set to false to make no backup when restoring (default = True)
        @param failOnNotFound: set to False if we don't want to fail if a file is not found (default is True)
        """
        if snapshot is None:
            raise exceptions.SBException("Please provide a Snapshot")
        if _file is None:
            raise exceptions.SBException("Please provide a File/directory")

        _file = self._fop.pathsep + _file.lstrip(self._fop.pathsep)
#        print "restore as: %s" % _file

        # restore
        if not snapshot.getSnapshotFileInfos().hasPath(_file) and not snapshot.getSnapshotFileInfos().hasFile(_file):
            if failOnNotFound:
                raise exceptions.SBException(_("File '%s' not found in the backup snapshot files list") % _file)
            else:
                self.logger.warning(_("File '%(filename)s' not found in snapshot's [%(snapshotname)s] files list, Skipped.")\
                                    % {"filename": _file, "snapshotname" : snapshot.getName()})
                return

        suffix = None
        if backupFlag :
            now = datetime.datetime.now().isoformat("_").replace(":", ".")
            suffix = ".before_restore_" + now

        if target and self._fop.path_exists(target):
            # The target is given and exists
            if self._fop.is_dir(target):
                # the target is a dir     
                #create a temp file , extract inside then move the content
                tmpdir = tempfile.mkdtemp(dir = target,
                                          prefix = 'nssbackup-restore_')

                tar.extract(snapshot.getArchive(),
                            _file,
                            tmpdir,
                            bckupsuffix = suffix,
                            splitsize = snapshot.getSplitedSize())

                if self._fop.path_exists(target + self._fop.pathsep + self._fop.get_basename(_file))  and backupFlag :
                    self._fop.force_move(target + self._fop.pathsep + self._fop.get_basename(_file),
                                   target + self._fop.pathsep + self._fop.get_basename(_file) + suffix)

                self._fop.force_move(tmpdir + _file, target + self._fop.pathsep + self._fop.get_basename(_file))
                self._fop.force_delete(tmpdir)
            else:
                #the target is a file
                parent = self._fop.get_dirname(target)
                tar.extract(snapshot.getArchive(), _file, parent, bckupsuffix = suffix, splitsize = snapshot.getSplitedSize())
        else:
            # target is set to None or target not exists
            if target and not self._fop.path_exists(target) :
                #target != None but target doesn't exists
#TODO: should we use makedir?
                self._fop.makedirs(target)
                tar.extract(snapshot.getArchive(), _file, target, splitsize = snapshot.getSplitedSize())
            else :
                # Target = None , extract at the place it belongs
                if self._fop.path_exists(_file) :
                    # file exist:
                    tar.extract(snapshot.getArchive(), _file, target, bckupsuffix = suffix, splitsize = snapshot.getSplitedSize())
                else :
                    # file doesn't exist nothing to move, just extract
                    tar.extract(snapshot.getArchive(), _file, target, splitsize = snapshot.getSplitedSize())


    def revert(self, snapshot, directory):
        """
        Revert a directory to its snapshot date state.
        @param snapshot : The snapshot from which to revert 
        @param dir : the dir to revert, use self._fop.pathsep for the whole snapshot
        """
        self.revertAs(snapshot, directory, None)


    def __cleanBackupedFiles(self, directory , suffix):
        """
        clean the backuped copies in the directory (dir) that ends with suffix
        @param dir: directory to clean up
        @param suffix: the suffix of backuped files
        """
        pass


    def revertAs(self, snapshot, directory, targetdir):
        """
        Revert a directory to its snapshot date state into a directory.
        We will restore the directory starting from the base snapshot to the selected one and clean the restore directory each time.
        @param snapshot : The snapshot from which to revert 
        @param dir : the dir to revert, use self._fop.pathsep for the whole snapshot
        @param targetdir: The dir in which to restore files 
        """
        if not snapshot:
            raise exceptions.SBException("Please provide a Snapshot")
        if not directory:
            raise exceptions.SBException("Please provide a File/directory")

        snpman = SnapshotManager.SnapshotManager(self._fop.get_dirname(snapshot.getPath()))
        history = snpman.getSnpHistory(snapshot)
        history.reverse()

        for snp in history :
            self.logger.debug("Restoring '%(dirname)s' from snapshot '%(snapshotname)s'"\
                              % { "dirname" : directory, "snapshotname" : snp.getName() })
            self.restoreAs(snapshot = snp, _file = directory, target = targetdir, backupFlag = False, failOnNotFound = False)