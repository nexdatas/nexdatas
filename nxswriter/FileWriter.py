#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
#

""" Provides abstraction for file writer """

#: writer module
writer = None


def open_file(filename, readonly=False):
    """ open the new file

    :param filename: file name
    :type filename: :obj:`str`
    :param readonly: readonly flag
    :type readonly: :obj:`bool`
    :returns: file object
    :rtype : :class:`FTFile`
    """
    return writer.open_file(filename, readonly)


def create_file(filename, overwrite=False):
    """ create a new file

    :param filename: file name
    :type filename: :obj:`str`
    :param overwrite: overwrite flag
    :type overwrite: :obj:`bool`
    :returns: file object
    :rtype : :class:`FTFile`
    """
    return writer.create_file(filename, overwrite)


def link(target, parent, name):
    """ create link

    :param target: file name
    :type target: :obj:`str`
    :param parent: parent object
    :type parent: :class:`FTObject`
    :param name: link name
    :type name: :obj:`str`
    :returns: link object
    :rtype : :class:`FTLink`
    """
    return writer.link(target, parent, name)


def deflate_filter():
    """ create deflate filter

    :returns: deflate filter object
    :rtype : :class:`FTDeflate`
    """
    return writer.deflate_filter()


class FTObject(object):
    """ virtual file tree object
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: tree parent
        :type tparent: :obj:`FTObject`
        """
        self._h5object = h5object
        self._tparent = tparent
        self.children = []

    def close(self):
        """ close element
        """
        for ch in self.children:
            if ch() is not None:
                ch().close()

    def _reopen(self):
        """ reopen elements and children
        """
        self.children = [ch for ch in self.children if ch() is not None]
        for ch in self.children:
            ch().reopen()

    @property
    def parent(self):
        """ return the parent object

        :returns: file tree group
        :rtype : :class:`FTGroup`
        """
        return self._tparent

    @property
    def h5object(self):
        """ provide object of native library

        :returns: pni object
        :rtype: :obj:`any`
        """
        return self._h5object

    @property
    def is_valid(self):
        """ check if attribute is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return True


class FTFile(FTObject):
    """ file tree file
    """

    def __init__(self, h5object, filename):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param filename:  file name
        :type filename: :obj:`str`
        """
        FTObject.__init__(self, h5object, None)
        #: (:obj:`str`) file name
        self.name = filename

    def root(self):
        """ root object

        :returns: parent object
        :rtype: :class:`FTGroup `
        """

    def flush(self):
        """ flash the data
        """

    @property
    def readonly(self):
        """ check if file is readonly

        :returns: readonly flag
        :rtype: :obj:`bool`
        """

    def reopen(self, readonly=False, swmr=False, libver=None):
        """ reopen attribute

        :param readonly: readonly flag
        :type readonly: :obj:`bool`
        :param swmr: swmr flag
        :type swmr: :obj:`bool`
        :param libver:  library version, default: 'latest'
        :type libver: :obj:`str`
        """
        FTObject._reopen(self)


class FTGroup(FTObject):
    """ file tree group
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FTObject.__init__(self, h5object, tparent)

    def open(self, name):
        """ open a file tree element

        :param name: element name
        :type name: :obj:`str`
        :returns: file tree object
        :rtype : :class:`FTObject`
        """

    def create_group(self, n, nxclass=""):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param nxclass: group type
        :type nxclass: :obj:`str`
        :returns: file tree group
        :rtype : :class:`FTGroup`
        """

    def create_field(self, name, type_code,
                     shape=None, chunk=None, dfilter=None):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param type_code: nexus field type
        :type type_code: :obj:`str`
        :param shape: shape
        :type shape: :obj:`list` < :obj:`int` >
        :param chunk: chunk
        :type chunk: :obj:`list` < :obj:`int` >
        :param dfilter: filter deflater
        :type dfilter: :class:`FTDeflate`
        :returns: file tree field
        :rtype : :class:`FTField`
        """

    @property
    def size(self):
        """ group size

        :returns: group size
        :rtype: :obj:`int`
        """

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype : :class:`FTAttributeManager`
        """

    def exists(self, name):
        """ if child exists

        :param name: child name
        :type name: :obj:`str`
        :returns: existing flag
        :rtype: :obj:`bool`
        """

    def reopen(self):
        """ reopen attribute
        """
        FTObject._reopen(self)


class FTField(FTObject):
    """ file tree file
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FTObject.__init__(self, h5object, tparent)

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype : :class:`FTAttributeManager`
        """

    def grow(self, dim=0, ext=1):
        """ grow the field

        :param dim: growing dimension
        :type dim: :obj:`int`
        :param dim: size of the grow
        :type dim: :obj:`int`
        """

    def read(self):
        """ read the field value

        :returns: pni object
        :rtype: :obj:`any`
        """

    def write(self, o):
        """ write the field value

        :param o: pni object
        :type o: :obj:`any`
        """

    def __setitem__(self, t, o):
        """ set value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: pni object
        :type o: :obj:`any`
        """

    def __getitem__(self, t):
        """ get value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :returns: pni object
        :rtype: :obj:`any`
        """

    @property
    def dtype(self):
        """ field data type

        :returns: field data type
        :rtype: :obj:`str`
        """

    @property
    def shape(self):
        """ field shape

        :returns: field shape
        :rtype: :obj:`list` < :obj:`int` >
        """

    @property
    def size(self):
        """ field size

        :returns: field size
        :rtype: :obj:`int`
        """

    def reopen(self):
        """ reopen attribute
        """
        FTObject._reopen(self)


class FTLink(FTObject):
    """ file tree link
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FTObject.__init__(self, h5object, tparent)

    @property
    def target_path(self):
        """ target path

        :returns: target path
        :rtype: :obj:`str`
        """

    def reopen(self):
        """ reopen attribute
        """
        FTObject._reopen(self)


class FTDeflate(FTObject):
    """ file tree deflate
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FTObject.__init__(self, h5object, tparent)

    @property
    def rate(self):
        """ getter for compression rate

        :returns: compression rate
        :rtype: :obj:`int`
        """

    @rate.setter
    def rate(self, value):
        """ setter for compression rate

        :param value: compression rate
        :type value: :obj:`int`
        """

    @property
    def shuffle(self):
        """ getter for compression shuffle

        :returns: compression shuffle
        :rtype: :obj:`bool`
        """

    @shuffle.setter
    def shuffle(self, value):
        """ setter for compression shuffle

        :param value: compression shuffle
        :type value: :obj:`bool`
        """

    def reopen(self):
        """ reopen attribute
        """
        FTObject._reopen(self)


class FTAttributeManager(FTObject):
    """ file tree attribute
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FTObject.__init__(self, h5object, tparent)

    def create(self, name, dtype, shape=None, overwrite=False):
        """ create a new attribute

        :param name: attribute name
        :type name: :obj:`str`
        :param dtype: attribute type
        :type dtype: :obj:`str`
        :param shape: attribute shape
        :type shape: :obj:`list` < :obj:`int` >
        :param overwrite: overwrite flag
        :type overwrite: :obj:`bool`
        :returns: attribute object
        :rtype : :class:`FTAtribute`
        """

    def __len__(self):
        """ number of attributes

        :returns: number of attributes
        :rtype: :obj:`int`
        """

    def __setitem__(self, name, o):
        """ set value

        :param name: attribute name
        :type name: :obj:`str`
        :param o: pni object
        :type o: :obj:`any`
        """

    def __getitem__(self, name):
        """ get value

        :param name: attribute name
        :type name: :obj:`str`
        :returns: attribute object
        :rtype : :class:`FTAtribute`
        """

    def reopen(self):
        """ reopen attribute
        """
        FTObject._reopen(self)


class FTAttribute(FTObject):
    """ virtual file tree attribute
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FTObject.__init__(self, h5object, tparent)

    def read(self):
        """ read attribute value

        :returns: python object
        :rtype: :obj:`any`
        """

    def write(self, o):
        """ write attribute value

        :param o: python object
        :type o: :obj:`any`
        """

    def __setitem__(self, t, o):
        """ write attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: python object
        :type o: :obj:`any`
        """

    def __getitem__(self, t):
        """ read attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :returns: python object
        :rtype: :obj:`any`
        """

    @property
    def dtype(self):
        """ attribute data type

        :returns: attribute data type
        :rtype: :obj:`str`
        """

    @property
    def shape(self):
        """ attribute shape

        :returns: attribute shape
        :rtype: :obj:`list` < :obj:`int` >
        """

    def reopen(self):
        """ reopen attribute
        """
        FTObject._reopen(self)
