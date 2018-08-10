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

""" Provides a pool  with data decoders """

import struct
import numpy


class UTF8decoder(object):

    """ UTF8 decoder
    """

    def __init__(self):
        """ constructor

        :brief: It clears the local variables
        """
        #: (:obj:`str`) decoder name
        self.name = "UTF8"
        #: (:obj:`str`) decoder format
        self.format = None
        #: (:obj:`str`) data type
        self.dtype = None

        #: (:class:`numpy.ndarray`) image data
        self.__value = None
        #: ([:obj:`str`, :obj:`str`]) header and image data
        self.__data = None

    def load(self, data):
        """ loads encoded data

        :param data: encoded data
        :type data: [:obj:`str`, :obj:`str`]
        """
        self.__data = data
        self.format = data[0]
        self.__value = None
        self.dtype = "string"

    def shape(self):
        """ provides the data shape

        :returns: the data shape i.e. `[1, 0]`
        :rtype: :obj:`list` <:obj:`int` >
        """
        return [1, 0]

    def decode(self):
        """ provides the decoded data

        :returns: the decoded data if data was loaded
        :rtype: :class:`numpy.ndarray`
        """
        if not self.__data:
            return
        if not self.__value:
            self.__value = self.__data[1]
        return self.__value


class UINT32decoder(object):

    """ INT decoder
    """

    def __init__(self):
        """ constructor

        :brief: It clears the local variables
        """
        #: (:obj:`str`) decoder name
        self.name = "UINT32"
        #: (:obj:`str`) decoder format
        self.format = None
        #: (:obj:`str`) data type
        self.dtype = None

        #: (:class:`numpy.ndarray`) image data
        self.__value = None
        #: ([:obj:`str`, :obj:`str`]) header and image data
        self.__data = None

    def load(self, data):
        """ loads encoded data

        :param data: encoded data
        :type data: [:obj:`str`, :obj:`str`]
        """
        if not hasattr(data, "__iter__"):
            raise ValueError("Wrong Data Format")
        if len(data[1]) % 4:
            raise ValueError("Wrong encoded UINT32 data length")
        self.__data = data
        self.format = data[0]
        self.__value = None
        self.dtype = "uint32"

    def shape(self):
        """ provides the data shape

        :returns: the data shape if data was loaded
        :rtype: :obj:`list` <:obj:`int` >
        """
        if self.__data:
            return [len(self.__data[1]) // 4, 0]

    def decode(self):
        """ provides the decoded data

        :returns: the decoded data if data was loaded
        :rtype: :class:`numpy.ndarray`

        """
        if not self.__data:
            return
        if len(self.__data[1]) % 4:
            raise ValueError("Wrong encoded UINT32 data length")
        if not self.__value:
            if isinstance(self.__data[1], str):
                data = bytearray()
                data.extend(map(ord, self.__data[1]))
            else:
                data = self.__data[1]
            res = struct.unpack('I' * (len(data) // 4), data)
            self.__value = numpy.array(
                struct.unpack('I' * (len(data) // 4), data),
                dtype=self.dtype).reshape(len(data) // 4)
        return self.__value


class VDEOdecoder(object):

    """ VIDEO IMAGE LIMA decoder
    """

    def __init__(self):
        """ constructor

        :brief: It clears the local variables
        """
        #: (:obj:`str`) decoder name
        self.name = "LIMA_VIDEO_IMAGE"
        #: (:obj:`str`) decoder format
        self.format = None
        #: (:obj:`str`) data type
        self.dtype = None

        #: (:class:`numpy.ndarray`) image data
        self.__value = None
        #: ([:obj:`str`, :obj:`str`]) header and image data
        self.__data = None
        #: (:obj:`str`) struct header format
        self.__headerFormat = '!IHHqiiHHHH'
        #: (:obj:`dict` <:obj:`str`, :obj:`any` > ) header data
        self.__header = {}
        #: (:obj:`dict` <:obj:`int`, :obj:`str` > ) format modes
        self.__formatID = {0: 'B', 1: 'H', 2: 'I', 3: 'Q'}
        #: (:obj:`dict` <:obj:`int`, :obj:`str` > ) dtype modes
        self.__dtypeID = {0: 'uint8', 1: 'uint16', 2: 'uint32', 3: 'uint64'}

    def load(self, data):
        """  loads encoded data

        :param data: encoded data
        :type data: [:obj:`str`, :obj:`str`]
        """
        self.__data = data
        self.format = data[0]
        self._loadHeader(data[1][:struct.calcsize(self.__headerFormat)])
        self.__value = None

    def _loadHeader(self, headerData):
        """ loads the image header

        :param headerData: buffer with header data
        :type headerData: :obj:`str`
        """
        hdr = struct.unpack(self.__headerFormat, headerData)
        self.__header = {}
        self.__header['magic'] = hdr[0]
        self.__header['headerVersion'] = hdr[1]
        self.__header['imageMode'] = hdr[2]
        self.__header['frameNumber'] = hdr[3]
        self.__header['width'] = hdr[4]
        self.__header['height'] = hdr[5]
        self.__header['endianness'] = hdr[6]
        self.__header['headerSize'] = hdr[7]
        self.__header['padding'] = hdr[7:]

        self.dtype = self.__dtypeID[self.__header['imageMode']]

    def shape(self):
        """ provides the data shape

        :returns: the data shape if data was loaded
        :rtype: :obj:`list` <:obj:`int` >
        """
        if self.__header:
            return [self.__header['width'], self.__header['height']]

    def decode(self):
        """ provides the decoded data

        :returns: the decoded data if data was loaded
        :rtype: :class:`numpy.ndarray`
        """
        if not self.__header or not self.__data:
            return
        if not self.__value:
            image = self.__data[1][struct.calcsize(self.__headerFormat):]
            dformat = self.__formatID[self.__header['imageMode']]
            fSize = struct.calcsize(dformat)
            self.__value = numpy.array(
                struct.unpack(dformat * (len(image) // fSize), image),
                dtype=self.dtype).reshape(self.__header['width'],
                                          self.__header['height'])
        return self.__value


class DecoderPool(object):

    """ Decoder pool
    """

    def __init__(self, configJSON=None):
        """ constructor

        :brief: It creates know decoders
        :param configJSON: string with decoders
        :type configJSON: \
        :    :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        self.__knowDecoders = {
            "LIMA_VIDEO_IMAGE": VDEOdecoder,
            "UTF8": UTF8decoder,
            "UINT32": UINT32decoder}
        self.__pool = {}

        self.__createDecoders()
        self.appendUserDecoders(configJSON)

    def appendUserDecoders(self, configJSON):
        """ loads user decoders

        :param configJSON: string with decoders
        :type configJSON: \
        :    :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if configJSON and 'decoders' in configJSON.keys() \
                and hasattr(configJSON['decoders'], 'keys'):
            for dk in configJSON['decoders'].keys():
                pkl = configJSON['decoders'][dk].split(".")
                dec = __import__(".".join(pkl[:-1]), globals(),
                                 locals(), pkl[-1])
                self.append(getattr(dec, pkl[-1]), dk)

    def __createDecoders(self):
        """ creates know decoders

        :brief: It calls constructor of know decoders
        """
        for dk in self.__knowDecoders.keys():
            self.__pool[dk] = self.__knowDecoders[dk]()

    def hasDecoder(self, decoder):
        """ checks it the decoder is registered

        :param decoder: the given decoder
        :type decoder: :obj:`str`
        :returns: True if it the decoder is registered
        :rtype: :obj:`bool`
        """
        return True if decoder in self.__pool.keys() else False

    def get(self, decoder):
        """ checks it the decoder is registered

        :param decoder: the given decoder
        :type decoder: :obj:`str`
        :returns: True if it the decoder is registered
        :rtype: :obj:`object`
        """
        if decoder in self.__pool.keys():
            return self.__pool[decoder]

    def pop(self, name):
        """ adds additional decoder

        :param name: name of the adding decoder
        :type name: :obj:`str`
        """
        self.__pool.pop(name, None)

    def append(self, decoder, name):
        """ adds additional decoder

        :param name: name of the adding decoder
        :type name: :obj:`str`
        :param decoder: instance of the adding decoder
        :type decoder: :obj:`object`
        :returns: name of decoder
        :rtype: :obj:`str`
        """

        instance = decoder()
        self.__pool[name] = instance

        if not hasattr(instance, "load") or not hasattr(instance, "name") \
                or not hasattr(instance, "shape") \
                or not hasattr(instance, "decode") \
                or not hasattr(instance, "dtype") \
                or not hasattr(instance, "format"):
            self.pop(name)
            return
        return name
