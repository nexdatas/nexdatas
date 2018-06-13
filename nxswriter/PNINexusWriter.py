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

""" Provides pni file writer """

import math
from pninexus import h5cpp
from pninexus import nexus

# import pni.io.nx.h5 as nx

from . import FileWriter


def _slice2selection(t):
    """ converts slice(s) to selection

    :param t: slice tuple
    :type t: :obj:`tuple`
    :returns: hyperslab selection
    :rtype: :class:`h5cpp.dataspace.Hyperslab`
    """

    if t is Ellipsis:
        return None
    elif isinstance(t, slice):
        if t.step in [None, 1]:
            return h5cpp.dataspace.Hyperslab(
                offset=(t.start,),
                block=(t.stop-t.start,))
        else:
            return h5cpp.dataspace.Hyperslab(
                offset=(t.start,),
                count=int(math.ceil((t.stop-t.start)/float(t.step))),
                stride=(t.step - 1,))
    elif isinstance(t, int):
        return h5cpp.dataspace.Hyperslab(
            offset=(t,), block=(1,))
    elif isinstance(t, list):
        offset = []
        block = []
        count = []
        stride = []
        for tel in t:
            if isinstance(tel, int):
                offset.append(tel)
                block.append(1)
                count.append(1)
                stride.append(0)
            elif isinstance(t, slice):
                if t.step in [None, 1]:
                    offset.append(tel.start)
                    block.append(tel.stop - tel.start)
                    count.append(1)
                    stride.append(0)
                else:
                    offset.append(tel.start)
                    block.append(1)
                    count.append(
                        int(math.ceil(
                            (tel.stop - tel.start) / float(tel.step))))
                    stride.append(tel.step - 1)
        if len(offset):
            return h5cpp.dataspace.Hyperslab(
                offset=offset, block=block, count=count, stride=stride)


pTh = {
    "long": h5cpp.datatype.Integer,
    "str": h5cpp.datatype.kVariableString,
    "unicode": h5cpp.datatype.kVariableString,
    "bool": h5cpp.datatype.Integer,
    "int": h5cpp.datatype.Integer,
    "int64": h5cpp.datatype.kInt64,
    "int32": h5cpp.datatype.kInt32,
    "int16": h5cpp.datatype.kIn16,
    "int8": h5cpp.datatype.kInt8,
    "uint": h5cpp.datatype.kInt64,
    "uint64": h5cpp.datatype.kUInt64,
    "uint32": h5cpp.datatype.kUInt32,
    "uint16": h5cpp.datatype.kUInt16,
    "uint8": h5cpp.datatype.kUInt8,
    "float": h5cpp.datatype.Float,
    "float64": h5cpp.datatype.Float64,
    "float32": h5cpp.datatype.Float32,
    "float16": h5cpp.datatype.Float16,
    "string": h5cpp.datatype.kVariableString
}


hTp = {
    h5cpp.datatype.Integer: "long",
    h5cpp.datatype.kVariableString: "string",
    h5cpp.datatype.kInt64: "int64",
    h5cpp.datatype.kInt32: "int32",
    h5cpp.datatype.kIn16: "int16",
    h5cpp.datatype.kInt8: "int8",
    h5cpp.datatype.kInt64: "uint",
    h5cpp.datatype.kUInt64: "uint64",
    h5cpp.datatype.kUInt32: "uint32",
    h5cpp.datatype.kUInt16: "uint16",
    h5cpp.datatype.kUInt8: "uint8",
    h5cpp.datatype.Float:  "float",
    h5cpp.datatype.Float64: "float64",
    h5cpp.datatype.Float32: "float32",
    h5cpp.datatype.Float16: "float16",
}


def open_file(filename, readonly=False, libver=None):
    """ open the new file

    :param filename: file name
    :type filename: :obj:`str`
    :param readonly: readonly flag
    :type readonly: :obj:`bool`
    :param libver: library version: 'lastest' or 'earliest'
    :type libver: :obj:`str`
    :returns: file object
    :rtype: :class:`PNINexusFile`
    """
    fapl = h5cpp.property.FileAccessList()
    flag = h5cpp.file.AccessFlags.READONLY if readonly \
        else h5cpp.file.AccessFlags.READWRITE
    if libver is None or libver == 'lastest':
        fapl.library_version_bounds(
            h5cpp.property.LibVersion.LATEST,
            h5cpp.property.LibVersion.LATEST)

    return PNINexusFile(h5cpp.file.open(filename, flag, fapl), filename)


def create_file(filename, overwrite=False, libver=None):
    """ create a new file

    :param filename: file name
    :type filename: :obj:`str`
    :param overwrite: overwrite flag
    :type overwrite: :obj:`bool`
    :param libver: library version: 'lastest' or 'earliest'
    :type libver: :obj:`str`
    :returns: file object
    :rtype: :class:`PNINexusFile`
    """
    fcpl = h5cpp.property.FileCreationList()
    fapl = h5cpp.property.FileAccessList()
    flag = h5cpp.file.AccessFlags.TRUNCATE if overwrite \
        else h5cpp.file.AccessFlags.EXCLUSIVE
    if libver is None or libver == 'lastest':
        fapl.library_version_bounds(
            h5cpp.property.LibVersion.LATEST,
            h5cpp.property.LibVersion.LATEST)
    return PNINexusFile(nexus.create_file(filename, flag, fcpl, fapl),
                        filename)


def link(target, parent, name):
    """ create link

    :param target: file name
    :type target: :obj:`str`
    :param parent: parent object
    :type parent: :class:`FTObject`
    :param name: link name
    :type name: :obj:`str`
    :returns: link object
    :rtype: :class:`PNINexusLink`
    """
    nexus.link(target, parent.h5object, name)
    lks = parent.h5object.links
    lk = [e for e in lks if str(e.path).split("/")[-1] == name][0]
    el = PNINexusLink(lk, parent)
    return el


def get_links(parent):
    """ get links

    :param parent: parent object
    :type parent: :class:`FTObject`
    :returns: list of link objects
    :returns: link object
    :rtype: :obj: `list` <:class:`PNINexusLink`>
    """
    lks = parent.h5object.links
    links = [PNINexusLink(e, parent) for e in lks]
    return links


def deflate_filter():
    """ create deflate filter

    :returns: deflate filter object
    :rtype: :class:`PNINexusDeflate`
    """
    return PNINexusDeflate(h5cpp.filter.Deflate())


class PNINexusFile(FileWriter.FTFile):

    """ file tree file
    """

    def __init__(self, h5object, filename):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param filename:  file name
        :type filename: :obj:`str`
        """
        FileWriter.FTFile.__init__(self, h5object, filename)
        #: (:obj:`str`) object nexus path
        self.path = None
        if hasattr(h5object, "path"):
            self.path = h5object.path

    def root(self):
        """ root object

        :returns: parent object
        :rtype: :class:`PNINexusGroup`
        """
        return PNINexusGroup(self._h5object.root(), self)

    def flush(self):
        """ flash the data
        """
        self._h5object.flush()

    def close(self):
        """ close file
        """
        FileWriter.FTFile.close(self)
        self._h5object.close()

    @property
    def is_valid(self):
        """ check if file is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.is_valid

    @property
    def readonly(self):
        """ check if file is readonly

        :returns: readonly flag
        :rtype: :obj:`bool`
        """
        return self._h5object.readonly

    def reopen(self, readonly=False, swmr=False, libver=None):
        """ reopen file

        :param readonly: readonly flag
        :type readonly: :obj:`bool`
        :param swmr: swmr flag
        :type swmr: :obj:`bool`
        :param libver:  library version, default: 'latest'
        :type libver: :obj:`str`
        """

        fapl = h5cpp.property.FileAccessList()
        if libver is None or libver == 'lastest' or swmr:
            fapl.library_version_bounds(
                h5cpp.property.LibVersion.LATEST,
                h5cpp.property.LibVersion.LATEST)

        if swmr:
            flag = h5cpp.file.AccessFlags.READWRITE \
                | h5cpp.file.AccessFlags.SWMRWRITE
        elif readonly:
            flag = h5cpp.file.AccessFlags.READONLY
        else:
            flag = h5cpp.file.AccessFlags.READWRITE

        self._h5object = nexus.open_file(self.name, flag, fapl)
        FileWriter.FTFile.reopen(self)


class PNINexusGroup(FileWriter.FTGroup):

    """ file tree group
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: tree parent
        :type tparent: :obj:`FTObject`
        """

        FileWriter.FTGroup.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.link.path
        if hasattr(h5object, "name"):
            self.name = str(h5object.link.path).split("/")[-1]

    def open(self, name):
        """ open a file tree element

        :param name: element name
        :type name: :obj:`str`
        :returns: file tree object
        :rtype: :class:`FTObject`
        """
        itm = nexus.get_objects(self._h5object,
                                nexus.Path(h5cpp.Path(name)))[0]
        if isinstance(itm, h5cpp._node.Dataset):
            el = PNINexusField(itm, self)
        elif isinstance(itm, h5cpp._node.Group):
            el = PNINexusGroup(itm, self)
        elif isinstance(itm, h5cpp._attribute.Attribute):
            el = PNINexusAttribute(itm, self)
        elif isinstance(itm, h5cpp._node.Link):
            el = PNINexusLink(itm, self)
        else:
            return FileWriter.FTObject(itm, self)
        return el

    def create_group(self, n, nxclass=""):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param nxclass: group type
        :type nxclass: :obj:`str`
        :returns: file tree group
        :rtype: :class:`PNINexusGroup`
        """
        return PNINexusGroup(
            nexus.BaseClassFactory.create(self._h5object, n, nxclass),
            self)

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
        :type dfilter: :class:`PNINexusDeflate`
        :returns: file tree field
        :rtype: :class:`PNINexusField`
        """

        dcpl = h5cpp.property.DatasetCreationList()
        if dfilter:
            dfilter.h5object(dcpl)
            if dfilter.shuffle:
                sfilter = h5cpp.filter.Shuffle()
                sfilter(dcpl)
        return PNINexusField(
            nexus.FieldFactory.create(
                self._h5object, name, type_code, shape,
                chunk=chunk, dcpl=dcpl),
            self
        )

    @property
    def size(self):
        """ group size

        :returns: group size
        :rtype: :obj:`int`
        """
        return self._h5object.links.size

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype: :class:`PNINexusAttributeManager`
        """
        return PNINexusAttributeManager(self._h5object.attributes, self)

    def close(self):
        """ close group
        """
        FileWriter.FTGroup.close(self)
        self._h5object.close()

    def reopen(self):
        """ reopen group
        """
        if isinstance(self._tparent, PNINexusFile):
            self._h5object = self._tparent.h5object.root()
        else:
            self._h5object = nexus.get_objects(
                self._tparent.h5object, nexus.Path(h5cpp.Path(self.name)))[0]
        FileWriter.FTGroup.reopen(self)

    def exists(self, name):
        """ if child exists

        :param name: child name
        :type name: :obj:`str`
        :returns: existing flag
        :rtype: :obj:`bool`
        """
        return name in [
            str(lk.path).split("/")[-1] for lk in self._h5object.links]

    def names(self):
        """ read the child names

        :returns: pni object
        :rtype: :obj:`list` <`str`>
        """
        return [
            str(lk.path).split("/")[-1] for lk in self._h5object.links]

    class PNINexusGroupIter(object):

        def __init__(self, group):
            """ constructor

            :param group: group object
            :type manager: :obj:`H5PYGroup`
            """

            self.__group = group
            self.__names = group.names

        def __next__(self):
            """ the next attribute

            :returns: attribute object
            :rtype: :class:`FTAtribute`
            """
            if self.__names:
                return self.__group.open(self.__names.pop(0))
            else:
                raise StopIteration()

        next = __next__

        def __iter__(self):
            """ attribute iterator

            :returns: attribute iterator
            :rtype: :class:`H5PYAttrIter`
            """
            return self

    def __iter__(self):
        """ attribute iterator

        :returns: attribute iterator
        :rtype: :class:`H5PYAttrIter`
        """
        return self.PNINexusGroupIter(self)

    @property
    def is_valid(self):
        """ check if field is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.is_valid


class PNINexusField(FileWriter.FTField):

    """ file tree file
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTField.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.link.path
        if hasattr(h5object, "name"):
            self.name = str(h5object.link.path).split("/")[-1]

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype: :class:`PNINexusAttributeManager`
        """
        return PNINexusAttributeManager(self._h5object.attributes, self)

    def close(self):
        """ close field
        """
        FileWriter.FTField.close(self)
        self._h5object.close()

    def reopen(self):
        """ reopen field
        """
        self._h5object = nexus.get_objects(
            self._tparent.h5object, nexus.Path(h5cpp.Path(self.name)))[0]
        FileWriter.FTField.reopen(self)

    def refresh(self):
        """ refresh the field

        :returns: refreshed
        :rtype: :obj:`bool`
        """
        self._h5object.refresh()
        return True

    def grow(self, dim=0, ext=1):
        """ grow the field

        :param dim: growing dimension
        :type dim: :obj:`int`
        :param dim: size of the grow
        :type dim: :obj:`int`
        """
        self._h5object.extent(dim, ext)

    def read(self):
        """ read the field value

        :returns: pni object
        :rtype: :obj:`any`
        """
        return self._h5object.read()

    def write(self, o):
        """ write the field value

        :param o: pni object
        :type o: :obj:`any`
        """
        self._h5object.write(o)

    def __setitem__(self, t, o):
        """ set value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: pni object
        :type o: :obj:`any`
        """
        selection = _slice2selection(t)
        self._h5object.__setitem__(t, o)
        if selection is None:
            self._h5object.write(o)
        else:
            self._h5object.write(o, selection=selection)

    def __getitem__(self, t):
        """ get value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :returns: pni object
        :rtype: :obj:`any`
        """
        selection = _slice2selection(t)
        if selection is None:
            return self._h5object.read()
        else:
            return self._h5object.read(selection=selection)

    @property
    def is_valid(self):
        """ check if field is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.is_valid

    @property
    def dtype(self):
        """ field data type

        :returns: field data type
        :rtype: :obj:`str`
        """
        return hTp[self._h5object.datatype.type]

    @property
    def shape(self):
        """ field shape

        :returns: field shape
        :rtype: :obj:`list` < :obj:`int` >
        """
        return self._h5object.dataspace.current_dimensions

    @property
    def size(self):
        """ field size

        :returns: field size
        :rtype: :obj:`int`
        """
        return self._h5object.dataspace.size


class PNINexusLink(FileWriter.FTLink):

    """ file tree link
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTLink.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = str(h5object.path).split("/")[-1]

    @property
    def is_valid(self):
        """ check if link is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object is not None and self._h5object.is_valid

    def refresh(self):
        """ refresh the field

        :returns: refreshed
        :rtype: :obj:`bool`
        """
        self._h5object.refresh()
        return True

    @classmethod
    def getfilename(cls, obj):
        filename = ""
        while not filename:
            par = obj.parent
            if par is None:
                break
            if isinstance(par, PNINexusFile):
                filename = par.name
                break
            else:
                obj = par
        return filename

    @property
    def target_path(self):
        """ target path

        :returns: target path
        :rtype: :obj:`str`
        """
        fpath = self._h5object.target().file_path
        opath = self._h5object.target().object_path
        if not fpath:
            fpath = self.getfilename(self)
        return "%s:/%s" % (fpath, opath)

    def reopen(self):
        """ reopen field
        """
        lks = self._tparent.h5object.links
        try:
            lk = [e for e in lks
                  if str(e.path).split("/")[-1] == self.name][0]
            self._h5object = lk
        except:
            self._h5object = None
        FileWriter.FTLink.reopen(self)

    def close(self):
        """ close group
        """
        FileWriter.FTLink.close(self)
        self._h5object = None


class PNINexusDeflate(FileWriter.FTDeflate):

    """ file tree deflate
    """

    def __init__(self, h5object):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        """
        FileWriter.FTDeflate.__init__(self, h5object)
        self.__shuffle = None

    def __getrate(self):
        """ getter for compression rate

        :returns: compression rate
        :rtype: :obj:`int`
        """
        return self._h5object.level

    def __setrate(self, value):
        """ setter for compression rate

        :param value: compression rate
        :type value: :obj:`int`
        """
        self._h5object.level = value

    #: (:obj:`int`) compression rate
    rate = property(__getrate, __setrate)

    def __getshuffle(self):
        """ getter for compression shuffle

        :returns: compression shuffle
        :rtype: :obj:`bool`
        """
        return self.__shuffle

    def __setshuffle(self, value):
        """ setter for compression shuffle

        :param value: compression shuffle
        :type value: :obj:`bool`
        """
        self.__shuffle = value

    #: (:obj:`bool`) compression shuffle
    shuffle = property(__getshuffle, __setshuffle)


class PNINexusAttributeManager(FileWriter.FTAttributeManager):

    """ file tree attribute
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTAttributeManager.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = ''
        #: (:obj:`str`) object name
        self.name = None

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
        :rtype: :class:`PNINexusAtribute`
        """
        names = [at.name for at in self._h5object.attributes]
        if name in names:
            if overwrite:
                self._h5object.remove(name)
            else:
                raise Exception("Attribute %s exists" % name)
        shape = shape or []
        if shape:
            return PNINexusAttribute(
                self._h5object.create(
                    name, pTh[dtype], shape), self.parent)
        else:
            return PNINexusAttribute(
                self._h5object.create(
                    name, pTh[dtype]), self.parent)

    def __len__(self):
        """ number of attributes

        :returns: number of attributes
        :rtype: :obj:`int`
        """
        return self._h5object.__len__()

    def __getitem__(self, name):
        """ get value

        :param name: attribute name
        :type name: :obj:`str`
        :returns: attribute object
        :rtype: :class:`FTAtribute`
        """
        return PNINexusAttribute(
            self._h5object.__getitem__(name), self.parent)

    def close(self):
        """ close attribure manager
        """
        FileWriter.FTAttributeManager.close(self)

    def reopen(self):
        """ reopen field
        """
        self._h5object = self._tparent.h5object.attributes
        FileWriter.FTAttributeManager.reopen(self)

    @property
    def is_valid(self):
        """ check if link is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return True


class PNINexusAttribute(FileWriter.FTAttribute):

    """ file tree attribute
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTAttribute.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    def close(self):
        """ close attribute
        """
        FileWriter.FTAttribute.close(self)
        self._h5object.close()

    def read(self):
        """ read attribute value

        :returns: python object
        :rtype: :obj:`any`
        """
        return self._h5object.read()

    def write(self, o):
        """ write attribute value

        :param o: python object
        :type o: :obj:`any`
        """
        self._h5object.write(o)

    def __setitem__(self, t, o):
        """ write attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: python object
        :type o: :obj:`any`
        """
        self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        """ read attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :returns: python object
        :rtype: :obj:`any`
        """
        return self._h5object.__getitem__(t)

    @property
    def is_valid(self):
        """ check if attribute is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.is_valid

    @property
    def dtype(self):
        """ attribute data type

        :returns: attribute data type
        :rtype: :obj:`str`
        """
        return hTp[self._h5object.datatype.type]

    @property
    def shape(self):
        """ attribute shape

        :returns: attribute shape
        :rtype: :obj:`list` < :obj:`int` >
        """
        if hasattr(self._h5object.dataspace, "current_dimensions"):
            return self._h5object.dataspace.current_dimensions
        else:
            []

    def reopen(self):
        """ reopen attribute
        """
        self._h5object = self._tparent.h5object.attributes[self.name]
        FileWriter.FTAttribute.reopen(self)
