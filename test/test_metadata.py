#!/usr/bin/python

#Audio Tools, a module and set of tools for manipulating audio data
#Copyright (C) 2007-2011  Brian Langenberger

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import unittest
import audiotools
import tempfile

from test import (parser, BLANK_PCM_Reader, Combinations,
                  TEST_COVER1, TEST_COVER2, TEST_COVER3, TEST_COVER4,
                  HUGE_BMP)

def do_nothing(self):
    pass

#add a bunch of decorator metafunctions like LIB_CORE
#which can be wrapped around individual tests as needed
for section in parser.sections():
    for option in parser.options(section):
        if (parser.getboolean(section, option)):
            vars()["%s_%s" % (section.upper(),
                              option.upper())] = lambda function: function
        else:
            vars()["%s_%s" % (section.upper(),
                              option.upper())] = lambda function: do_nothing

class MetaDataTest(unittest.TestCase):
    def setUp(self):
        self.metadata_class = audiotools.MetaData
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "media",
                                 "ISRC",
                                 "catalog",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "date",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = []

    def empty_metadata(self):
        return self.metadata_class()

    @METADATA_METADATA
    def test_roundtrip(self):
        for audio_class in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_class.SUFFIX)
            try:
                track = audio_class.from_pcm(temp_file.name,
                                             BLANK_PCM_Reader(1))
                metadata = self.empty_metadata()
                setattr(metadata, self.supported_fields[0], u"Foo")
                track.set_metadata(metadata)
                metadata2 = track.get_metadata()
                self.assertEqual(self.metadata_class, metadata2.__class__)

                #also ensure that the new track is playable
                audiotools.transfer_framelist_data(track.to_pcm(), lambda f: f)
            finally:
                temp_file.close()

    @METADATA_METADATA
    def test_attribs(self):
        import string
        import random

        #a nice sampling of Unicode characters
        chars = u"".join(map(unichr,
                             range(0x30, 0x39 + 1) +
                             range(0x41, 0x5A + 1) +
                             range(0x61, 0x7A + 1) +
                             range(0xC0, 0x17E + 1) +
                             range(0x18A, 0x1EB + 1) +
                             range(0x3041, 0x3096 + 1) +
                             range(0x30A1, 0x30FA + 1)))

        for audio_class in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_class.SUFFIX)
            try:
                track = audio_class.from_pcm(temp_file.name,
                                             BLANK_PCM_Reader(1))

                #check that setting the fields to random values works
                for field in self.supported_fields:
                    metadata = self.empty_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        unicode_string = u"".join(
                            [random.choice(chars)
                             for i in xrange(random.choice(range(1, 21)))])
                        setattr(metadata, field, unicode_string)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field),
                                         unicode_string)
                    else:
                        number = random.choice(range(1, 100))
                        setattr(metadata, field, number)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), number)

                #check that blanking out the fields works
                for field in self.supported_fields:
                    metadata = self.empty_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        setattr(metadata, field, u"")
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), u"")
                    else:
                        setattr(metadata, field, 0)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), 0)

                #re-set the fields with random values
                for field in self.supported_fields:
                    metadata = self.empty_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        unicode_string = u"".join(
                            [random.choice(chars)
                             for i in xrange(random.choice(range(1, 21)))])
                        setattr(metadata, field, unicode_string)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field),
                                         unicode_string)
                    else:
                        number = random.choice(range(1, 100))
                        setattr(metadata, field, number)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), number)

                    #check that deleting the fields works
                    delattr(metadata, field)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        self.assertEqual(getattr(metadata, field), u"")
                    else:
                        self.assertEqual(getattr(metadata, field), 0)

            finally:
                temp_file.close()

    @METADATA_METADATA
    def test_field_mapping(self):
        #ensure that setting a class field
        #updates its corresponding low-level implementation

        #ensure that updating the low-level implementation
        #is reflected in the class field

        pass

    @METADATA_METADATA
    def test_foreign_field(self):
        pass

    @METADATA_METADATA
    def test_converted(self):
        #build a generic MetaData with everything
        image1 = audiotools.Image.new(TEST_COVER1, "Text 1", 0)
        image2 = audiotools.Image.new(TEST_COVER2, "Text 2", 1)
        image3 = audiotools.Image.new(TEST_COVER3, "Text 3", 2)

        metadata_orig = audiotools.MetaData(track_name=u"a",
                                            track_number=1,
                                            track_total=2,
                                            album_name=u"b",
                                            artist_name=u"c",
                                            performer_name=u"d",
                                            composer_name=u"e",
                                            conductor_name=u"f",
                                            media=u"g",
                                            ISRC=u"h",
                                            catalog=u"i",
                                            copyright=u"j",
                                            publisher=u"k",
                                            year=u"l",
                                            date=u"m",
                                            album_number=3,
                                            album_total=4,
                                            comment="n",
                                            images=[image1, image2, image3])

        #ensure converted() builds something with our class
        metadata_new = self.metadata_class.converted(metadata_orig)
        self.assertEqual(metadata_new.__class__, self.metadata_class)

        #ensure our fields match
        for field in audiotools.MetaData.__FIELDS__:
            if (field in self.supported_fields):
                self.assertEqual(getattr(metadata_orig, field),
                                 getattr(metadata_new, field))
            elif (field in audiotools.MetaData.__INTEGER_FIELDS__):
                self.assertEqual(getattr(metadata_new, field), 0)
            else:
                self.assertEqual(getattr(metadata_new, field), u"")

        #ensure images match, if supported
        if (self.metadata_class.supports_images()):
            self.assertEqual(metadata_new.images(),
                             [image1, image2, image3])

        #subclasses should ensure non-MetaData fields are converted

    @METADATA_METADATA
    def test_supports_images(self):
        self.assertEqual(self.metadata_class.supports_images(), True)

    @METADATA_METADATA
    def test_images(self):
        #perform tests only if images are actually supported
        if (self.metadata_class.supports_images()):
            for audio_class in self.supported_formats:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix="." + audio_class.SUFFIX)
                try:
                    track = audio_class.from_pcm(temp_file.name,
                                                 BLANK_PCM_Reader(1))

                    metadata = self.empty_metadata()
                    self.assertEqual(metadata.images(), [])

                    image1 = audiotools.Image.new(TEST_COVER1,
                                                  u"Text 1", 0)
                    image2 = audiotools.Image.new(TEST_COVER2,
                                                  u"Text 2", 1)
                    image3 = audiotools.Image.new(TEST_COVER3,
                                                  u"Text 3", 2)

                    track.set_metadata(metadata)
                    metadata = track.get_metadata()

                    #ensure that adding one image works
                    metadata.add_image(image1)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    self.assertEqual(metadata.images(), [image1])

                    #ensure that adding a second image works
                    metadata.add_image(image2)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    self.assertEqual(metadata.images(), [image1,
                                                         image2])

                    #ensure that adding a third image works
                    metadata.add_image(image3)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    self.assertEqual(metadata.images(), [image1,
                                                         image2,
                                                         image3])

                    #ensure that deleting the first image works
                    metadata.delete_image(image1)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    self.assertEqual(metadata.images(), [image2,
                                                         image3])

                    #ensure that deleting the second image works
                    metadata.delete_image(image2)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    self.assertEqual(metadata.images(), [image3])

                    #ensure that deleting the third image works
                    metadata.delete_image(image3)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    self.assertEqual(metadata.images(), [])

                finally:
                    temp_file.close()

    @METADATA_METADATA
    def test_merge(self):
        import random

        def field_val(field, value, int_value):
            if (field in audiotools.MetaData.__INTEGER_FIELDS__):
                return int_value
            else:
                return value

        for audio_class in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_class.SUFFIX)
            try:
                track = audio_class.from_pcm(temp_file.name,
                                             BLANK_PCM_Reader(1))

                for i in xrange(10):
                    shuffled_fields = self.supported_fields[:]
                    random.shuffle(shuffled_fields)

                    for (range_a, range_b) in [
                        ((0, len(shuffled_fields) / 3), #no overlap
                         (-(len(shuffled_fields) / 3),
                           len(shuffled_fields) + 1)),

                        ((0, len(shuffled_fields) / 2), #partial overlap
                         (len(shuffled_fields) / 4,
                          len(shuffled_fields) / 4 + len(shuffled_fields) / 2)),

                        ((0, len(shuffled_fields) / 3), #complete overlap
                         (0, len(shuffled_fields) / 3))]:
                        fields_a = shuffled_fields[range_a[0]:range_a[1]]
                        fields_b = shuffled_fields[range_b[0]:range_b[1]]

                        metadata_a = audiotools.MetaData(**dict([
                                    (field, field_val(field, u"a", 1))
                                    for field in fields_a]))
                        metadata_b = audiotools.MetaData(**dict([
                                    (field, field_val(field, u"b", 2))
                                    for field in fields_b]))

                        #ensure that metadata round-trips properly
                        track.delete_metadata()
                        track.set_metadata(metadata_a)
                        metadata_c = track.get_metadata()
                        self.assertEqual(metadata_c, metadata_a)
                        metadata_c.merge(metadata_b)
                        track.set_metadata(metadata_c)
                        metadata_c = track.get_metadata()

                        #ensure that the individual fields merge properly
                        for field in self.supported_fields:
                            if (field in fields_a):
                                if (field in
                                    audiotools.MetaData.__INTEGER_FIELDS__):
                                    self.assertEqual(
                                        getattr(metadata_c, field), 1)
                                else:
                                    self.assertEqual(
                                        getattr(metadata_c, field), u"a")
                            elif (field in fields_b):
                                if (field in
                                    audiotools.MetaData.__INTEGER_FIELDS__):
                                    self.assertEqual(
                                        getattr(metadata_c, field), 2)
                                else:
                                    self.assertEqual(
                                        getattr(metadata_c, field), u"b")
                            else:
                                if (field in
                                    audiotools.MetaData.__INTEGER_FIELDS__):
                                    self.assertEqual(
                                        getattr(metadata_c, field), 0)
                                else:
                                    self.assertEqual(
                                        getattr(metadata_c, field), u"")

                #ensure that embedded images merge properly
                if (self.metadata_class.supports_images()):
                    image1 = audiotools.Image.new(TEST_COVER1, u"", 0)
                    image2 = audiotools.Image.new(TEST_COVER2, u"", 0)

                    #if metadata_a has images and metadata_b has images
                    #metadata_a.merge(metadata_b) results in
                    #only metadata_a's images remaining
                    metadata_a = self.empty_metadata()
                    metadata_b = self.empty_metadata()
                    metadata_a.add_image(image1)
                    track.set_metadata(metadata_a)
                    metadata_a = track.get_metadata()
                    metadata_b.add_image(image2)
                    metadata_a.merge(metadata_b)
                    self.assertEqual(len(metadata_a.images()), 1)
                    self.assertEqual(metadata_a.images(), [image1])
                    track.set_metadata(metadata_a)
                    metadata_a = track.get_metadata()
                    self.assertEqual(metadata_a.images(), [image1])

                    #if metadata_a has no images and metadata_b has images
                    #metadata_a.merge(metadata_b) results in
                    #only metadata_b's images remaining
                    metadata_a = self.empty_metadata()
                    metadata_b = self.empty_metadata()
                    track.set_metadata(metadata_a)
                    metadata_a = track.get_metadata()
                    metadata_b.add_image(image2)
                    metadata_a.merge(metadata_b)
                    self.assertEqual(len(metadata_a.images()), 1)
                    self.assertEqual(metadata_a.images(), [image2])
                    track.set_metadata(metadata_a)
                    metadata_a = track.get_metadata()
                    self.assertEqual(metadata_a.images(), [image2])

                    #if metadata_a has images and metadata_b has no images
                    #metadata_a.merge(metadata_b) results in
                    #only metadata_a's images remaining
                    metadata_a = self.empty_metadata()
                    metadata_b = self.empty_metadata()
                    metadata_a.add_image(image1)
                    track.set_metadata(metadata_a)
                    metadata_a = track.get_metadata()
                    metadata_a.merge(metadata_b)
                    self.assertEqual(len(metadata_a.images()), 1)
                    self.assertEqual(metadata_a.images(), [image1])
                    track.set_metadata(metadata_a)
                    metadata_a = track.get_metadata()
                    self.assertEqual(metadata_a.images(), [image1])

            finally:
                temp_file.close()


class WavPackApeTagMetaData(MetaDataTest):
    def setUp(self):
        self.metadata_class = audiotools.WavPackAPEv2
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "ISRC",
                                 "catalog",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "date",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = [audiotools.WavPackAudio]

    def empty_metadata(self):
        return self.metadata_class.converted(audiotools.MetaData())

    @METADATA_WAVPACK
    def test_foreign_field(self):
        metadata = audiotools.WavePackAPEv2(
        [audiotools.ApeTagItem(0, False, "Title", 'Track Name'),
         audiotools.ApeTagItem(0, False, "Album", 'Album Name'),
         audiotools.ApeTagItem(0, False, "Track", "1/3"),
         audiotools.ApeTagItem(0, False, "Media", "2/4"),
         audiotools.ApeTagItem(0, False, "Foo", "Bar")])
        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name,
                                        BLANK_PCM_Reader(1))
                track.set_metadata(metadata)
                metadata2 = track.get_metadata()
                self.assertEqual(metadata, metadata2)
                self.assertEqual(metadata.__class__, metadata2.__class__)
                self.assertEqual(unicode(metadata2["Foo"]), u"Bar")
            finally:
                temp_file.close()

    @METADATA_WAVPACK
    def test_field_mapping(self):
        mapping = [('track_name', 'Title', u'a'),
                   ('album_name', 'Album', u'b'),
                   ('artist_name', 'Artist', u'c'),
                   ('performer_name', 'Performer', u'd'),
                   ('composer_name', 'Composer', u'e'),
                   ('conductor_name', 'Conductor', u'f'),
                   ('ISRC', 'ISRC', u'g'),
                   ('catalog', 'Catalog', u'h'),
                   ('publisher', 'Publisher', u'i'),
                   ('year', 'Year', u'j'),
                   ('date', 'Record Date', u'k'),
                   ('comment', 'Comment', u'l')]

        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name, BLANK_PCM_Reader(1))

                #ensure that setting a class field
                #updates its corresponding low-level implementation
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    setattr(metadata, field, value)
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(unicode(metadata[key]), unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata2, field), value)
                    self.assertEqual(unicode(metadata2[key]), unicode(value))

                #ensure that updating the low-level implementation
                #is reflected in the class field
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    metadata[key] = audiotools.ApeTagItem.string(
                        key, unicode(value))
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(unicode(metadata[key]), unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(unicode(metadata[key]), unicode(value))

                #ensure that setting numerical fields also
                #updates the low-level implementation
                track.delete_metadata()
                metadata = self.empty_metadata()
                metadata.track_number = 1
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['Track']), u'1')
                metadata.track_total = 2
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['Track']), u'1/2')
                del(metadata.track_number)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['Track']), u'0/2')
                del(metadata.track_total)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertRaises(KeyError,
                                  metadata.__getitem__,
                                  'Track')

                track.delete_metadata()
                metadata = self.empty_metadata()
                metadata.album_number = 3
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['Media']), u'3')
                metadata.album_total = 4
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['Media']), u'3/4')
                del(metadata.album_number)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['Media']), u'0/4')
                del(metadata.album_total)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertRaises(KeyError,
                                  metadata.__getitem__,
                                  'Media')

                #and ensure updating the low-level implementation
                #updates the numerical fields
                track.delete_metadata()
                metadata = self.empty_metadata()
                metadata['Track'] = audiotools.ApeTagItem.string(
                        'Track', u"1")
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.track_number, 1)
                self.assertEqual(metadata.track_total, 0)
                metadata['Track'] = audiotools.ApeTagItem.string(
                        'Track', u"1/2")
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.track_number, 1)
                self.assertEqual(metadata.track_total, 2)
                metadata['Track'] = audiotools.ApeTagItem.string(
                        'Track', u"0/2")
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.track_number, 0)
                self.assertEqual(metadata.track_total, 2)
                del(metadata['Track'])
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.track_number, 0)
                self.assertEqual(metadata.track_total, 0)

                track.delete_metadata()
                metadata = self.empty_metadata()
                metadata['Media'] = audiotools.ApeTagItem.string(
                        'Media', u"3")
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.album_number, 3)
                self.assertEqual(metadata.album_total, 0)
                metadata['Media'] = audiotools.ApeTagItem.string(
                        'Media', u"3/4")
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.album_number, 3)
                self.assertEqual(metadata.album_total, 4)
                metadata['Media'] = audiotools.ApeTagItem.string(
                        'Media', u"0/4")
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.album_number, 0)
                self.assertEqual(metadata.album_total, 4)
                del(metadata['Media'])
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.album_number, 0)
                self.assertEqual(metadata.album_total, 0)

            finally:
                temp_file.close()

    @METADATA_WAVPACK
    def test_converted(self):
        #build a generic MetaData with everything
        image1 = audiotools.Image.new(TEST_COVER1, "Text 1", 0)
        image2 = audiotools.Image.new(TEST_COVER2, "Text 2", 1)

        metadata_orig = audiotools.MetaData(track_name=u"a",
                                            track_number=1,
                                            track_total=2,
                                            album_name=u"b",
                                            artist_name=u"c",
                                            performer_name=u"d",
                                            composer_name=u"e",
                                            conductor_name=u"f",
                                            media=u"g",
                                            ISRC=u"h",
                                            catalog=u"i",
                                            copyright=u"j",
                                            publisher=u"k",
                                            year=u"l",
                                            date=u"m",
                                            album_number=3,
                                            album_total=4,
                                            comment="n",
                                            images=[image1, image2])

        #ensure converted() builds something with our class
        metadata_new = self.metadata_class.converted(metadata_orig)
        self.assertEqual(metadata_new.__class__, self.metadata_class)

        #ensure our fields match
        for field in audiotools.MetaData.__FIELDS__:
            if (field in self.supported_fields):
                self.assertEqual(getattr(metadata_orig, field),
                                 getattr(metadata_new, field))
            elif (field in audiotools.MetaData.__INTEGER_FIELDS__):
                self.assertEqual(getattr(metadata_new, field), 0)
            else:
                self.assertEqual(getattr(metadata_new, field), u"")

        #ensure images match, if supported
        self.assertEqual(metadata_new.images(), [image1, image2])

        #ensure non-MetaData fields are converted
        metadata_orig = self.empty_metadata()
        metadata_orig['Foo'] = audiotools.ApeTagItem.string(
            'Foo', u'Bar'.encode('utf-8'))
        metadata_new = self.metadata_class.converted(metadata_orig)
        self.assertEqual(metadata_orig['Foo'].data,
                         metadata_new['Foo'].data)

    @METADATA_WAVPACK
    def test_images(self):
        for audio_class in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_class.SUFFIX)
            try:
                track = audio_class.from_pcm(temp_file.name,
                                             BLANK_PCM_Reader(1))

                metadata = self.empty_metadata()
                self.assertEqual(metadata.images(), [])

                image1 = audiotools.Image.new(TEST_COVER1,
                                              u"Text 1", 0)
                image2 = audiotools.Image.new(TEST_COVER2,
                                              u"Text 2", 1)

                track.set_metadata(metadata)
                metadata = track.get_metadata()

                #ensure that adding one image works
                metadata.add_image(image1)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.images(), [image1])

                #ensure that adding a second image works
                metadata.add_image(image2)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.images(), [image1,
                                                     image2])

                #ensure that deleting the first image works
                metadata.delete_image(image1)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.images(), [image2])

                #ensure that deleting the second image works
                metadata.delete_image(image2)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.images(), [])

            finally:
                temp_file.close()

    @METADATA_WAVPACK
    def test_clean(self):
        #check trailing whitespace
        metadata = audiotools.WavPackAPEv2(
            [audiotools.ApeTagItem.string('Title', u'Foo ')])
        self.assertEqual(metadata.track_name, u'Foo ')
        self.assertEqual(metadata['Title'].data, u'Foo '.encode('ascii'))
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":'Title'.decode('ascii')}])
        self.assertEqual(cleaned.track_name, u'Foo')
        self.assertEqual(cleaned['Title'].data, u'Foo'.encode('ascii'))

        #check leading whitespace
        metadata = audiotools.WavPackAPEv2(
            [audiotools.ApeTagItem.string('Title', u' Foo')])
        self.assertEqual(metadata.track_name, u' Foo')
        self.assertEqual(metadata['Title'].data, u' Foo'.encode('ascii'))
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading whitespace from %(field)s") %
                          {"field":'Title'.decode('ascii')}])
        self.assertEqual(cleaned.track_name, u'Foo')
        self.assertEqual(cleaned['Title'].data, u'Foo'.encode('ascii'))

        #check empty fields
        metadata = audiotools.WavPackAPEv2(
            [audiotools.ApeTagItem.string('Title', u'')])
        self.assertEqual(metadata.track_name, u'')
        self.assertEqual(metadata['Title'].data, u''.encode('ascii'))
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed empty field %(field)s") %
                          {"field":'Title'.decode('ascii')}])
        self.assertEqual(cleaned.track_name, u'')
        self.assertRaises(KeyError,
                          cleaned.__getitem__,
                          'Title')

        #check leading zeroes
        metadata = audiotools.WavPackAPEv2(
            [audiotools.ApeTagItem.string('Track', u'01')])
        self.assertEqual(metadata.track_number, 1)
        self.assertEqual(metadata.track_total, 0)
        self.assertEqual(metadata['Track'].data, u'01'.encode('ascii'))
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading zeroes from %(field)s") %
                          {"field":'Track'.decode('ascii')}])
        self.assertEqual(cleaned.track_number, 1)
        self.assertEqual(cleaned.track_total, 0)
        self.assertEqual(cleaned['Track'].data, u'1'.encode('ascii'))

        metadata = audiotools.WavPackAPEv2(
            [audiotools.ApeTagItem.string('Track', u'01/2')])
        self.assertEqual(metadata.track_number, 1)
        self.assertEqual(metadata.track_total, 2)
        self.assertEqual(metadata['Track'].data, u'01/2'.encode('ascii'))
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading zeroes from %(field)s") %
                          {"field":'Track'.decode('ascii')}])
        self.assertEqual(cleaned.track_number, 1)
        self.assertEqual(cleaned.track_total, 2)
        self.assertEqual(cleaned['Track'].data, u'1/2'.encode('ascii'))

        metadata = audiotools.WavPackAPEv2(
            [audiotools.ApeTagItem.string('Track', u'1/02')])
        self.assertEqual(metadata.track_number, 1)
        self.assertEqual(metadata.track_total, 2)
        self.assertEqual(metadata['Track'].data, u'1/02'.encode('ascii'))
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading zeroes from %(field)s") %
                          {"field":'Track'.decode('ascii')}])
        self.assertEqual(cleaned.track_number, 1)
        self.assertEqual(cleaned.track_total, 2)
        self.assertEqual(cleaned['Track'].data, u'1/2'.encode('ascii'))

        metadata = audiotools.WavPackAPEv2(
            [audiotools.ApeTagItem.string('Track', u'01/02')])
        self.assertEqual(metadata.track_number, 1)
        self.assertEqual(metadata.track_total, 2)
        self.assertEqual(metadata['Track'].data, u'01/02'.encode('ascii'))
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading zeroes from %(field)s") %
                          {"field":'Track'.decode('ascii')}])
        self.assertEqual(cleaned.track_number, 1)
        self.assertEqual(cleaned.track_total, 2)
        self.assertEqual(cleaned['Track'].data, u'1/2'.encode('ascii'))

        #images don't store metadata,
        #so no need to check their fields


class ID3v1MetaData(MetaDataTest):
    def setUp(self):
        self.metadata_class = audiotools.ID3v1Comment
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "album_name",
                                 "artist_name",
                                 "year",
                                 "comment"]
        self.supported_formats = [audiotools.MP3Audio,
                                  audiotools.MP2Audio]

    def empty_metadata(self):
        return self.metadata_class(track_name=u"",
                                   artist_name=u"",
                                   album_name=u"",
                                   year=u"",
                                   comment=u"",
                                   track_number=0,
                                   genre=0)

    @METADATA_ID3V1
    def test_supports_images(self):
        self.assertEqual(self.metadata_class.supports_images(), False)

    @METADATA_ID3V1
    def test_attribs(self):
        import string
        import random

        #ID3v1 only supports ASCII characters
        #and not very many of them
        chars = u"".join(map(unichr,
                             range(0x30, 0x39 + 1) +
                             range(0x41, 0x5A + 1) +
                             range(0x61, 0x7A + 1)))

        for audio_class in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_class.SUFFIX)
            try:
                track = audio_class.from_pcm(temp_file.name,
                                             BLANK_PCM_Reader(1))

                #check that setting the fields to random values works
                for field in self.supported_fields:
                    metadata = self.empty_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        unicode_string = u"".join(
                            [random.choice(chars)
                             for i in xrange(random.choice(range(1, 5)))])
                        setattr(metadata, field, unicode_string)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field),
                                         unicode_string)
                    else:
                        number = random.choice(range(1, 100))
                        setattr(metadata, field, number)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), number)

                #check that blanking out the fields works
                for field in self.supported_fields:
                    metadata = self.empty_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        setattr(metadata, field, u"")
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), u"")
                    else:
                        setattr(metadata, field, 0)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), 0)

                #re-set the fields with random values
                for field in self.supported_fields:
                    metadata = self.empty_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        unicode_string = u"".join(
                            [random.choice(chars)
                             for i in xrange(random.choice(range(1, 5)))])
                        setattr(metadata, field, unicode_string)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field),
                                         unicode_string)
                    else:
                        number = random.choice(range(1, 100))
                        setattr(metadata, field, number)
                        track.set_metadata(metadata)
                        metadata = track.get_metadata()
                        self.assertEqual(getattr(metadata, field), number)

                #check that deleting the fields works
                for field in self.supported_fields:
                    metadata = self.empty_metadata()
                    delattr(metadata, field)
                    track.set_metadata(metadata)
                    metadata = track.get_metadata()
                    if (field not in audiotools.MetaData.__INTEGER_FIELDS__):
                        self.assertEqual(getattr(metadata, field), u"")
                    else:
                        self.assertEqual(getattr(metadata, field), 0)

            finally:
                temp_file.close()

    @METADATA_ID3V1
    def test_field_mapping(self):
        mapping = [('track_name', u'a'),
                   ('artist_name', u'b'),
                   ('album_name', u'c'),
                   ('year', u'1234'),
                   ('comment', u'd'),
                   ('track_number', 1)]

        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name, BLANK_PCM_Reader(1))

                #ensure that setting a class field
                #updates its corresponding low-level implementation
                for (field, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    setattr(metadata, field, value)
                    self.assertEqual(getattr(metadata, field), value)
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata2, field), value)

                #ID3v1 no longer has a low-level implementation
                #since it builds and parses directly on strings
            finally:
                temp_file.close()

    @METADATA_ID3V1
    def test_clean(self):
        #check trailing whitespace
        metadata = audiotools.ID3v1Comment(
            track_name=u"Title ",
            artist_name=u"",
            album_name=u"",
            year=u"",
            comment=u"",
            track_number=1,
            genre=0)
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(results,
                         [_(u"removed trailing whitespace from title")])
        self.assertEqual(
            cleaned,
            audiotools.ID3v1Comment(
                track_name=u"Title",
                artist_name=u"",
                album_name=u"",
                year=u"",
                comment=u"",
                track_number=1,
                genre=0))

        #check leading whitespace
        metadata = audiotools.ID3v1Comment(
                track_name=u" Title",
                artist_name=u"",
                album_name=u"",
                year=u"",
                comment=u"",
                track_number=1,
                genre=0)
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(results,
                         [_(u"removed leading whitespace from title")])
        self.assertEqual(
            cleaned,
            audiotools.ID3v1Comment(
                    track_name=u"Title",
                    artist_name=u"",
                    album_name=u"",
                    year=u"",
                    comment=u"",
                    track_number=1,
                    genre=0))

        #ID3v1 has no empty fields, image data or leading zeroes
        #so those can be safely ignored


class ID3v22MetaData(MetaDataTest):
    def setUp(self):
        self.metadata_class = audiotools.ID3v22Comment
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "media",
                                 "ISRC",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "date",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = [audiotools.MP3Audio,
                                  audiotools.MP2Audio,
                                  audiotools.AiffAudio]

    def empty_metadata(self):
        return self.metadata_class([])

    @METADATA_ID3V2
    def test_foreign_field(self):
        metadata = audiotools.ID3v22Comment(
            [audiotools.ID3v22TextFrame("TT2", 0, "Track Name"),
             audiotools.ID3v22TextFrame("TAL", 0, "Album Name"),
             audiotools.ID3v22TextFrame("TRK", 0, "1/3"),
             audiotools.ID3v22TextFrame("TPA", 0, "2/4"),
             audiotools.ID3v22TextFrame("TFO", 0, "Bar")])
        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name,
                                        BLANK_PCM_Reader(1))
                track.set_metadata(metadata)
                metadata2 = track.get_metadata()
                self.assertEqual(metadata, metadata2)
                self.assertEqual(metadata.__class__, metadata2.__class__)
                self.assertEqual(metadata["TFO"][0].string, "Bar")
            finally:
                temp_file.close()

    @METADATA_ID3V2
    def test_field_mapping(self):
        id3_class = self.metadata_class

        INTEGER_ATTRIBS = ('track_number',
                           'track_total',
                           'album_number',
                           'album_total')

        attribs1 = {}  # a dict of attribute -> value pairs ("track_name":u"foo")
        attribs2 = {}  # a dict of ID3v2 -> value pairs     ("TT2":u"foo")
        for (i, (attribute, key)) in enumerate(id3_class.ATTRIBUTE_MAP.items()):
            if (attribute not in INTEGER_ATTRIBS):
                attribs1[attribute] = attribs2[key] = u"value %d" % (i)
        attribs1["track_number"] = 2
        attribs1["track_total"] = 10
        attribs1["album_number"] = 1
        attribs1["album_total"] = 3

        id3 = id3_class.converted(audiotools.MetaData(**attribs1))

        #ensure that all the attributes match up
        for (attribute, value) in attribs1.items():
            self.assertEqual(getattr(id3, attribute), value)

        #ensure that all the keys for non-integer items match up
        for (key, value) in attribs2.items():
            self.assertEqual(unicode(id3[key][0]), value)

        #ensure the keys for integer items match up
        self.assertEqual(int(id3[id3_class.INTEGER_ITEMS[0]][0]),
                         attribs1["track_number"])
        self.assertEqual(id3[id3_class.INTEGER_ITEMS[0]][0].total(),
                         attribs1["track_total"])
        self.assertEqual(int(id3[id3_class.INTEGER_ITEMS[1]][0]),
                         attribs1["album_number"])
        self.assertEqual(id3[id3_class.INTEGER_ITEMS[1]][0].total(),
                         attribs1["album_total"])

        #ensure that changing attributes changes the underlying frame
        #>>> id3.track_name = u"bar"
        #>>> id3['TT2'][0] == u"bar"
        for (i, (attribute, key)) in enumerate(id3_class.ATTRIBUTE_MAP.items()):
            if (key not in id3_class.INTEGER_ITEMS):
                setattr(id3, attribute, u"new value %d" % (i))
                self.assertEqual(unicode(id3[key][0]), u"new value %d" % (i))

        #ensure that changing integer attributes changes the underlying frame
        #>>> id3.track_number = 2
        #>>> id3['TRK'][0] == u"2"
        id3.track_number = 3
        id3.track_total = 0
        self.assertEqual(unicode(id3[id3_class.INTEGER_ITEMS[0]][0]), u"3")

        id3.track_total = 8
        self.assertEqual(unicode(id3[id3_class.INTEGER_ITEMS[0]][0]), u"3/8")

        id3.album_number = 2
        id3.album_total = 0
        self.assertEqual(unicode(id3[id3_class.INTEGER_ITEMS[1]][0]), u"2")

        id3.album_total = 4
        self.assertEqual(unicode(id3[id3_class.INTEGER_ITEMS[1]][0]), u"2/4")

        #reset and re-check everything for the next round
        id3 = id3_class.converted(audiotools.MetaData(**attribs1))

        #ensure that all the attributes match up
        for (attribute, value) in attribs1.items():
            self.assertEqual(getattr(id3, attribute), value)

        for (key, value) in attribs2.items():
            if (key not in id3_class.INTEGER_ITEMS):
                self.assertEqual(unicode(id3[key][0]), value)
            else:
                self.assertEqual(int(id3[key][0]), value)

        #ensure that changing the underlying frames changes attributes
        #>>> id3['TT2'] = [u"bar"]
        #>>> id3.track_name == u"bar"
        for (i, (attribute, key)) in enumerate(id3_class.ATTRIBUTE_MAP.items()):
            if (attribute not in INTEGER_ATTRIBS):
                id3[key] = [u"new value %d" % (i)]
                self.assertEqual(getattr(id3, attribute),
                                 u"new value %d" % (i))

        #ensure that changing the underlying integer frames changes attributes
        id3[id3_class.INTEGER_ITEMS[0]] = [7]
        self.assertEqual(id3.track_number, 7)

        id3[id3_class.INTEGER_ITEMS[0]] = [u"8/9"]
        self.assertEqual(id3.track_number, 8)
        self.assertEqual(id3.track_total, 9)

        id3[id3_class.INTEGER_ITEMS[1]] = [4]
        self.assertEqual(id3.album_number, 4)

        id3[id3_class.INTEGER_ITEMS[1]] = [u"5/6"]
        self.assertEqual(id3.album_number, 5)
        self.assertEqual(id3.album_total, 6)

        #finally, just for kicks, ensure that explicitly setting
        #frames also changes attributes
        #>>> id3['TT2'] = [id3_class.TextFrame.from_unicode('TT2',u"foo")]
        #>>> id3.track_name = u"foo"
        for (i, (attribute, key)) in enumerate(id3_class.ATTRIBUTE_MAP.items()):
            if (attribute not in INTEGER_ATTRIBS):
                id3[key] = [id3_class.TextFrame.from_unicode(key, unicode(i))]
                self.assertEqual(getattr(id3, attribute), unicode(i))

        #and ensure explicitly setting integer frames also changes attribs
        id3[id3_class.INTEGER_ITEMS[0]] = [
            id3_class.TextFrame.from_unicode(id3_class.INTEGER_ITEMS[0],
                                             u"4")]
        self.assertEqual(id3.track_number, 4)
        self.assertEqual(id3.track_total, 0)

        id3[id3_class.INTEGER_ITEMS[0]] = [
            id3_class.TextFrame.from_unicode(id3_class.INTEGER_ITEMS[0],
                                             u"2/10")]
        self.assertEqual(id3.track_number, 2)
        self.assertEqual(id3.track_total, 10)

        id3[id3_class.INTEGER_ITEMS[1]] = [
            id3_class.TextFrame.from_unicode(id3_class.INTEGER_ITEMS[1],
                                             u"3")]
        self.assertEqual(id3.album_number, 3)
        self.assertEqual(id3.album_total, 0)

        id3[id3_class.INTEGER_ITEMS[1]] = [
            id3_class.TextFrame.from_unicode(id3_class.INTEGER_ITEMS[1],
                                             u"5/7")]
        self.assertEqual(id3.album_number, 5)
        self.assertEqual(id3.album_total, 7)

    @METADATA_ID3V2
    def test_clean(self):
        #check trailing whitespace
        metadata = audiotools.ID3v22Comment(
            [audiotools.ID3v22TextFrame.from_unicode("TT2", u"Title ")])
        self.assertEqual(metadata.track_name, u"Title ")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TT2"}])
        self.assertEqual(cleaned.track_name, u"Title")

        #check leading whitespace
        metadata = audiotools.ID3v22Comment(
            [audiotools.ID3v22TextFrame.from_unicode("TT2", u" Title")])
        self.assertEqual(metadata.track_name, u" Title")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading whitespace from %(field)s") %
                          {"field":u"TT2"}])
        self.assertEqual(cleaned.track_name, u"Title")

        #check empty fields
        metadata = audiotools.ID3v22Comment(
            [audiotools.ID3v22TextFrame.from_unicode("TT2", u"")])
        self.assertEqual(metadata["TT2"][0].string, u"")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed empty field %(field)s") %
                          {"field":u"TT2"}])
        self.assertRaises(KeyError,
                          cleaned.__getitem__,
                          "TT2")

        #check leading zeroes,
        #depending on whether we're preserving them or not
        if (audiotools.config.getboolean_default("ID3", "pad", False)):
            #pad ID3v2 tags with 0
            metadata = audiotools.ID3v22Comment(
                [audiotools.ID3v22TextFrame.from_unicode("TRK", u"1")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 0)
            self.assertEqual(metadata["TRK"][0].string, u"1")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"added leading zeroes to %(field)s") %
                              {"field":u"TRK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 0)
            self.assertEqual(cleaned["TRK"][0].string, u"01")

            metadata = audiotools.ID3v22Comment(
                [audiotools.ID3v22TextFrame.from_unicode("TRK", u"1/2")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRK"][0].string, u"1/2")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"added leading zeroes to %(field)s") %
                              {"field":u"TRK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRK"][0].string, u"01/02")
        else:
            #don't pad ID3v2 tags with 0
            metadata = audiotools.ID3v22Comment(
                [audiotools.ID3v22TextFrame.from_unicode("TRK", u"01")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 0)
            self.assertEqual(metadata["TRK"][0].string, u"01")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 0)
            self.assertEqual(cleaned["TRK"][0].string, u"1")

            metadata = audiotools.ID3v22Comment(
                [audiotools.ID3v22TextFrame.from_unicode("TRK", u"01/2")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRK"][0].string, u"01/2")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRK"][0].string, u"1/2")

            metadata = audiotools.ID3v22Comment(
                [audiotools.ID3v22TextFrame.from_unicode("TRK", u"1/02")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRK"][0].string, u"1/02")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRK"][0].string, u"1/2")

            metadata = audiotools.ID3v22Comment(
                [audiotools.ID3v22TextFrame.from_unicode("TRK", u"01/02")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRK"][0].string, u"01/02")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRK"][0].string, u"1/2")


class ID3v23MetaData(ID3v22MetaData):
    def setUp(self):
        self.metadata_class = audiotools.ID3v23Comment
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "media",
                                 "ISRC",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "date",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = [audiotools.MP3Audio,
                                  audiotools.MP2Audio]

    @METADATA_ID3V2
    def test_foreign_field(self):
        metadata = self.metadata_class(
            [audiotools.ID3v23TextFrame("TIT2", 0, "Track Name"),
             audiotools.ID3v23TextFrame("TALB", 0, "Album Name"),
             audiotools.ID3v23TextFrame("TRCK", 0, "1/3"),
             audiotools.ID3v23TextFrame("TPOS", 0, "2/4"),
             audiotools.ID3v23TextFrame("TFOO", 0, "Bar")])
        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name,
                                        BLANK_PCM_Reader(1))
                track.set_metadata(metadata)
                metadata2 = track.get_metadata()
                self.assertEqual(metadata, metadata2)
                self.assertEqual(metadata.__class__, metadata2.__class__)
                self.assertEqual(metadata["TFOO"][0].string, "Bar")
            finally:
                temp_file.close()

    def empty_metadata(self):
        return self.metadata_class([])

    @METADATA_ID3V2
    def test_clean(self):
        #check trailing whitespace
        metadata = audiotools.ID3v23Comment(
            [audiotools.ID3v23TextFrame.from_unicode("TIT2", u"Title ")])
        self.assertEqual(metadata.track_name, u"Title ")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TIT2"}])
        self.assertEqual(cleaned.track_name, u"Title")

        #check leading whitespace
        metadata = audiotools.ID3v23Comment(
            [audiotools.ID3v23TextFrame.from_unicode("TIT2", u" Title")])
        self.assertEqual(metadata.track_name, u" Title")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading whitespace from %(field)s") %
                          {"field":u"TIT2"}])
        self.assertEqual(cleaned.track_name, u"Title")

        #check empty fields
        metadata = audiotools.ID3v23Comment(
            [audiotools.ID3v23TextFrame.from_unicode("TIT2", u"")])
        self.assertEqual(metadata["TIT2"][0].string, u"")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed empty field %(field)s") %
                          {"field":u"TIT2"}])
        self.assertRaises(KeyError,
                          cleaned.__getitem__,
                          "TIT2")

        #check leading zeroes,
        #depending on whether we're preserving them or not
        if (audiotools.config.getboolean_default("ID3", "pad", False)):
            #pad ID3v2 tags with 0
            metadata = audiotools.ID3v23Comment(
                [audiotools.ID3v23TextFrame.from_unicode("TRCK", u"1")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 0)
            self.assertEqual(metadata["TRCK"][0].string, u"1")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"added leading zeroes to %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 0)
            self.assertEqual(cleaned["TRCK"][0].string, u"01")

            metadata = audiotools.ID3v23Comment(
                [audiotools.ID3v23TextFrame.from_unicode("TRCK", u"1/2")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"1/2")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"added leading zeroes to %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"01/02")
        else:
            #don't pad ID3v2 tags with 0
            metadata = audiotools.ID3v23Comment(
                [audiotools.ID3v23TextFrame.from_unicode("TRCK", u"01")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 0)
            self.assertEqual(metadata["TRCK"][0].string, u"01")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 0)
            self.assertEqual(cleaned["TRCK"][0].string, u"1")

            metadata = audiotools.ID3v23Comment(
                [audiotools.ID3v23TextFrame.from_unicode("TRCK", u"01/2")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"01/2")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"1/2")

            metadata = audiotools.ID3v23Comment(
                [audiotools.ID3v23TextFrame.from_unicode("TRCK", u"1/02")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"1/02")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"1/2")

            metadata = audiotools.ID3v23Comment(
                [audiotools.ID3v23TextFrame.from_unicode("TRCK", u"01/02")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"01/02")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"1/2")

        #check mislabeled images
        metadata = audiotools.ID3v23Comment(
            [audiotools.ID3v23PicFrame("""iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKAQMAAAC3/F3+AAAAAXNSR0IArs4c6QAAAANQTFRF////
p8QbyAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sEBBMWM3PnvjMAAAALSURBVAjXY2DA
BwAAHgABboVHMgAAAABJRU5ErkJggg==""".decode('base64'),
                                       u"image/jpeg",
                                       u"",
                                       3)])
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"fixed embedded image metadata fields")])
        self.assertEqual(cleaned.images()[0],
                         audiotools.Image.new("""iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKAQMAAAC3/F3+AAAAAXNSR0IArs4c6QAAAANQTFRF////
p8QbyAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sEBBMWM3PnvjMAAAALSURBVAjXY2DA
BwAAHgABboVHMgAAAABJRU5ErkJggg==""".decode('base64'),
                                              u"",
                                              0))


class ID3v24MetaData(ID3v22MetaData):
    def setUp(self):
        self.metadata_class = audiotools.ID3v23Comment
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "media",
                                 "ISRC",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "date",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = [audiotools.MP3Audio,
                                  audiotools.MP2Audio]

    def empty_metadata(self):
        return self.metadata_class([])

    @METADATA_ID3V2
    def test_clean(self):
       #check trailing whitespace
        metadata = audiotools.ID3v24Comment(
            [audiotools.ID3v24TextFrame.from_unicode("TIT2", u"Title ")])
        self.assertEqual(metadata.track_name, u"Title ")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TIT2"}])
        self.assertEqual(cleaned.track_name, u"Title")

        #check leading whitespace
        metadata = audiotools.ID3v24Comment(
            [audiotools.ID3v24TextFrame.from_unicode("TIT2", u" Title")])
        self.assertEqual(metadata.track_name, u" Title")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed leading whitespace from %(field)s") %
                          {"field":u"TIT2"}])
        self.assertEqual(cleaned.track_name, u"Title")

        #check empty fields
        metadata = audiotools.ID3v24Comment(
            [audiotools.ID3v24TextFrame.from_unicode("TIT2", u"")])
        self.assertEqual(metadata["TIT2"][0].string, u"")
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"removed empty field %(field)s") %
                          {"field":u"TIT2"}])
        self.assertRaises(KeyError,
                          cleaned.__getitem__,
                          "TIT2")

        #check leading zeroes,
        #depending on whether we're preserving them or not
        if (audiotools.config.getboolean_default("ID3", "pad", False)):
            #pad ID3v2 tags with 0
            metadata = audiotools.ID3v24Comment(
                [audiotools.ID3v24TextFrame.from_unicode("TRCK", u"1")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 0)
            self.assertEqual(metadata["TRCK"][0].string, u"1")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"added leading zeroes to %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 0)
            self.assertEqual(cleaned["TRCK"][0].string, u"01")

            metadata = audiotools.ID3v24Comment(
                [audiotools.ID3v24TextFrame.from_unicode("TRCK", u"1/2")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"1/2")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"added leading zeroes to %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"01/02")
        else:
            #don't pad ID3v2 tags with 0
            metadata = audiotools.ID3v24Comment(
                [audiotools.ID3v24TextFrame.from_unicode("TRCK", u"01")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 0)
            self.assertEqual(metadata["TRCK"][0].string, u"01")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 0)
            self.assertEqual(cleaned["TRCK"][0].string, u"1")

            metadata = audiotools.ID3v24Comment(
                [audiotools.ID3v24TextFrame.from_unicode("TRCK", u"01/2")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"01/2")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"1/2")

            metadata = audiotools.ID3v24Comment(
                [audiotools.ID3v24TextFrame.from_unicode("TRCK", u"1/02")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"1/02")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"1/2")

            metadata = audiotools.ID3v24Comment(
                [audiotools.ID3v24TextFrame.from_unicode("TRCK", u"01/02")])
            self.assertEqual(metadata.track_number, 1)
            self.assertEqual(metadata.track_total, 2)
            self.assertEqual(metadata["TRCK"][0].string, u"01/02")
            fixes = []
            cleaned = metadata.clean(fixes)
            self.assertEqual(fixes,
                             [_(u"removed leading zeroes from %(field)s") %
                              {"field":u"TRCK"}])
            self.assertEqual(cleaned.track_number, 1)
            self.assertEqual(cleaned.track_total, 2)
            self.assertEqual(cleaned["TRCK"][0].string, u"1/2")

        #check mislabeled images
        metadata = audiotools.ID3v24Comment(
            [audiotools.ID3v24PicFrame("""iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKAQMAAAC3/F3+AAAAAXNSR0IArs4c6QAAAANQTFRF////
p8QbyAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sEBBMWM3PnvjMAAAALSURBVAjXY2DA
BwAAHgABboVHMgAAAABJRU5ErkJggg==""".decode('base64'),
                                       u"image/jpeg",
                                       u"",
                                       3)])
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_(u"fixed embedded image metadata fields")])
        self.assertEqual(cleaned.images()[0],
                         audiotools.Image.new("""iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKAQMAAAC3/F3+AAAAAXNSR0IArs4c6QAAAANQTFRF////
p8QbyAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sEBBMWM3PnvjMAAAALSURBVAjXY2DA
BwAAHgABboVHMgAAAABJRU5ErkJggg==""".decode('base64'),
                                              u"",
                                              0))


class ID3CommentPairMetaData(MetaDataTest):
    def setUp(self):
        self.metadata_class = audiotools.ID3CommentPair
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "media",
                                 "ISRC",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "date",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = [audiotools.MP3Audio,
                                  audiotools.MP2Audio]

    def empty_metadata(self):
        return self.metadata_class.converted(audiotools.MetaData())

    @METADATA_ID3V2
    def test_field_mapping(self):
        pass


class FlacMetaData(MetaDataTest):
    def setUp(self):
        self.metadata_class = audiotools.FlacMetaData
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "media",
                                 "ISRC",
                                 "catalog",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        # self.supported_formats = [audiotools.FlacAudio,
        #                           audiotools.OggFlacAudio] #FIXME
        self.supported_formats = [audiotools.FlacAudio]

    def empty_metadata(self):
        return self.metadata_class.converted(audiotools.MetaData())

    @METADATA_FLAC
    def test_foreign_field(self):
        metadata = audiotools.FlacMetaData(
            vorbis_comment=audiotools.Flac_VORBISCOMMENT(
                        {"TITLE": [u'Track Name'],
                         "ALBUM": [u'Album Name'],
                         "TRACKNUMBER": [u"1"],
                         "TRACKTOTAL": [u"3"],
                         "DISCNUMBER": [u"2"],
                         "DISCTOTAL": [u"4"],
                         "FOO": [u"Bar"]}))
        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name,
                                        BLANK_PCM_Reader(1))
                track.set_metadata(metadata)
                metadata2 = track.get_metadata()
                self.assertEqual(metadata, metadata2)
                self.assertEqual(metadata.__class__, metadata2.__class__)
                self.assertEqual(track.get_metadata().vorbis_comment["FOO"],
                                 [u"Bar"])
            finally:
                temp_file.close()

    @METADATA_FLAC
    def test_field_mapping(self):
        mapping = [('track_name', 'TITLE', u'a'),
                   ('track_number', 'TRACKNUMBER', 1),
                   ('track_total', 'TRACKTOTAL', 2),
                   ('album_name', 'ALBUM', u'b'),
                   ('artist_name', 'ARTIST', u'c'),
                   ('performer_name', 'PERFORMER', u'd'),
                   ('composer_name', 'COMPOSER', u'e'),
                   ('conductor_name', 'CONDUCTOR', u'f'),
                   ('media', 'SOURCE MEDIUM', u'g'),
                   ('ISRC', 'ISRC', u'h'),
                   ('catalog', 'CATALOG', u'i'),
                   ('copyright', 'COPYRIGHT', u'j'),
                   ('year', 'DATE', u'k'),
                   ('album_number', 'DISCNUMBER', 3),
                   ('album_total', 'DISCTOTAL', 4),
                   ('comment', 'COMMENT', u'l')]

        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name, BLANK_PCM_Reader(1))

                #ensure that setting a class field
                #updates its corresponding low-level implementation
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    setattr(metadata, field, value)
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(
                        metadata.vorbis_comment[key][0],
                        unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata2, field), value)
                    self.assertEqual(
                        metadata2.vorbis_comment[key][0],
                        unicode(value))

                #ensure that updating the low-level implementation
                #is reflected in the class field
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    metadata.vorbis_comment[key] = [unicode(value)]
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(
                        metadata.vorbis_comment[key][0],
                        unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata2, field), value)
                    self.assertEqual(
                        metadata2.vorbis_comment[key][0],
                        unicode(value))
            finally:
                # temp_file.close()
                pass

    @METADATA_FLAC
    def test_converted(self):
        MetaDataTest.test_converted(self)

        metadata_orig = self.empty_metadata()
        metadata_orig.vorbis_comment['FOO'] = [u'bar']

        self.assertEqual(metadata_orig.vorbis_comment['FOO'], [u'bar'])

        metadata_new = self.metadata_class.converted(metadata_orig)

        self.assertEqual(metadata_orig.vorbis_comment['FOO'],
                         metadata_new.vorbis_comment['FOO'])

    @METADATA_FLAC
    def test_oversized(self):
        oversized_image = audiotools.Image.new(HUGE_BMP.decode('bz2'), u'', 0)
        oversized_text = "QlpoOTFBWSZTWYmtEk8AgICBAKAAAAggADCAKRoBANIBAOLuSKcKEhE1okng".decode('base64').decode('bz2').decode('ascii')

        for audio_class in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_class.SUFFIX)
            try:
                track = audio_class.from_pcm(temp_file.name,
                                             BLANK_PCM_Reader(1))

                #check that setting an oversized field fails properly
                metadata = self.empty_metadata()
                metadata.track_name = oversized_text
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertNotEqual(metadata.track_name, oversized_text)

                #check that setting an oversized image fails properly
                metadata = self.empty_metadata()
                metadata.add_image(oversized_image)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertNotEqual(metadata.images(), [oversized_image])

                #check that merging metadata with an oversized field
                #fails properly
                metadata = self.empty_metadata()
                metadata.merge(audiotools.MetaData(track_name=oversized_text))
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertNotEqual(metadata.track_name, oversized_text)

                #check that merging metadata with an oversized image
                #fails properly

                #FIXME
            finally:
                temp_file.close()

    @METADATA_FLAC
    def test_totals(self):
        metadata = self.empty_metadata()
        metadata.vorbis_comment["TRACKNUMBER"] = [u"2/4"]
        self.assertEqual(metadata.track_number, 2)
        self.assertEqual(metadata.track_total, 4)

        metadata = self.empty_metadata()
        metadata.vorbis_comment["DISCNUMBER"] = [u"1/3"]
        self.assertEqual(metadata.album_number, 1)
        self.assertEqual(metadata.album_total, 3)

    @METADATA_FLAC
    def test_clean(self):
        #check trailing whitespace
        metadata = audiotools.FlacMetaData(
            vorbis_comment=audiotools.Flac_VORBISCOMMENT(
                        {"TITLE": [u'Foo ']}))
        self.assertEqual(metadata.track_name, u'Foo ')
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned.track_name, u'Foo')
        self.assertEqual(results,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TITLE"}])

        #check leading whitespace
        metadata = audiotools.FlacMetaData(
            vorbis_comment=audiotools.Flac_VORBISCOMMENT(
                        {"TITLE": [u' Foo']}))
        self.assertEqual(metadata.track_name, u' Foo')
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned.track_name, u'Foo')
        self.assertEqual(results,
                         [_(u"removed leading whitespace from %(field)s") %
                          {"field":u"TITLE"}])

        #check leading zeroes
        metadata = audiotools.FlacMetaData(
            vorbis_comment=audiotools.Flac_VORBISCOMMENT(
                        {"TRACKNUMBER": [u'01']}))
        self.assertEqual(metadata.vorbis_comment["TRACKNUMBER"],[u"01"])
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned.vorbis_comment["TRACKNUMBER"],[u"1"])
        self.assertEqual(results,
                         [_(u"removed leading zeroes from %(field)s") %
                          {"field":u"TRACKNUMBER"}])

        #check empty fields
        metadata = audiotools.FlacMetaData(
                vorbis_comment=audiotools.Flac_VORBISCOMMENT(
                        {"TITLE": [u'  ']}))
        self.assertEqual(metadata.vorbis_comment["TITLE"], [u'  '])
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned,
                         audiotools.FlacMetaData(
                        vorbis_comment=audiotools.Flac_VORBISCOMMENT({})))
        self.assertEqual(results,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TITLE"},
                          _(u"removed empty field %(field)s") %
                          {"field":u"TITLE"}])

        #check mis-tagged images
        metadata = audiotools.FlacMetaData(
                    pictures=[audiotools.Flac_PICTURE(
                        0, "image/jpeg", u"", 20, 20, 24, 10,
"""iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKAQMAAAC3/F3+AAAAAXNSR0IArs4c6QAAAANQTFRF////
p8QbyAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9sEBBMWM3PnvjMAAAALSURBVAjXY2DA
BwAAHgABboVHMgAAAABJRU5ErkJggg==""".decode('base64'))])
        self.assertEqual(len(metadata.pictures), 1)
        image = metadata.images()[0]
        self.assertEqual(image.mime_type, "image/jpeg")
        self.assertEqual(image.width, 20)
        self.assertEqual(image.height, 20)
        self.assertEqual(image.color_depth, 24)
        self.assertEqual(image.color_count, 10)

        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(results,
                         [_(u"fixed embedded image metadata fields")])
        self.assertEqual(len(cleaned.pictures), 1)
        image = cleaned.images()[0]
        self.assertEqual(image.mime_type, "image/png")
        self.assertEqual(image.width, 10)
        self.assertEqual(image.height, 10)
        self.assertEqual(image.color_depth, 8)
        self.assertEqual(image.color_count, 1)


        #check that cleanup doesn't disturb other metadata blocks
        #FIXME
        metadata = audiotools.FlacMetaData(
            streaminfo=audiotools.Flac_STREAMINFO(
                minimum_block_size=4096,
                maximum_block_size=4096,
                minimum_frame_size=14,
                maximum_frame_size=18,
                sample_rate=44100,
                channels=2,
                bits_per_sample=16,
                total_samples=149606016L,
                md5sum='\xae\x87\x1c\x8e\xe1\xfc\x16\xde' +
                '\x86\x81&\x8e\xc8\xd52\xff'),
            applications=[audiotools.Flac_APPLICATION(
                application_id="FOOZ",
                data="KELP")],
            seektable=audiotools.Flac_SEEKTABLE([
                (0L, 0L, 4096),
                (8335360L, 30397L, 4096),
                (8445952L, 30816L, 4096),
                (17379328L, 65712L, 4096),
                (17489920L, 66144L, 4096),
                (28041216L, 107360L, 4096),
                (28151808L, 107792L, 4096),
                (41672704L, 160608L, 4096),
                (41783296L, 161040L, 4096),
                (54444032L, 210496L, 4096),
                (54558720L, 210944L, 4096),
                (65687552L, 254416L, 4096),
                (65802240L, 254864L, 4096),
                (76267520L, 295744L, 4096),
                (76378112L, 296176L, 4096),
                (89624576L, 347920L, 4096),
                (89739264L, 348368L, 4096),
                (99688448L, 387232L, 4096),
                (99803136L, 387680L, 4096),
                (114176000L, 443824L, 4096),
                (114286592L, 444256L, 4096),
                (125415424L, 487728L, 4096),
                (125526016L, 488160L, 4096),
                (138788864L, 539968L, 4096),
                (138903552L, 540416L, 4096)]),
            vorbis_comment=audiotools.Flac_VORBISCOMMENT({"TITLE":[u"Foo "]}),
            cuesheet=audiotools.Flac_CUESHEET(
                catalog_number='4560248013904\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                lead_in_samples=88200L,
                is_cdda=1,
                tracks=[
                    audiotools.Flac_CUESHEET_track(
                        offset=0L,
                        number=1,
                        ISRC='JPK631002201',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=8336076L,
                        number=2,
                        ISRC='JPK631002202',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=17379516L,
                        number=3,
                        ISRC='JPK631002203',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=28042308L,
                        number=4,
                        ISRC='JPK631002204',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=41672736L,
                        number=5,
                        ISRC='JPK631002205',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=54447624L,
                        number=6,
                        ISRC='JPK631002206',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=65689596L,
                        number=7,
                        ISRC='JPK631002207',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=76267716L,
                        number=8,
                        ISRC='JPK631002208',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=89627076L,
                        number=9,
                        ISRC='JPK631002209',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=99691872L,
                        number=10,
                        ISRC='JPK631002210',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=114176076L,
                        number=11,
                        ISRC='JPK631002211',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(113484L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=125415696L,
                        number=12,
                        ISRC='JPK631002212',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(114072L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=138791520L,
                        number=13,
                        ISRC='JPK631002213',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[
                            audiotools.Flac_CUESHEET_index(0L, 0),
                            audiotools.Flac_CUESHEET_index(114072L, 1)]),
                    audiotools.Flac_CUESHEET_track(
                        offset=149606016L,
                        number=170,
                        ISRC='\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                        track_type=0,
                        pre_emphasis=0,
                        index_points=[])]),
            pictures=[audiotools.Flac_PICTURE(0, "image/jpeg", u"",
                                              500, 500, 24, 0, TEST_COVER1)])


        self.assert_(metadata.streaminfo is not None)
        self.assert_(metadata.vorbis_comment is not None)
        self.assert_(metadata.seektable is not None)
        self.assert_(metadata.cuesheet is not None)
        self.assertEqual(len(metadata.pictures), 1)
        self.assertEqual(len(metadata.applications), 1)

        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(results,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TITLE"}])

        self.assertEqual(cleaned.streaminfo, metadata.streaminfo)
        self.assertEqual(cleaned.seektable, metadata.seektable)
        self.assertEqual(cleaned.cuesheet, metadata.cuesheet)
        self.assertEqual(cleaned.pictures, metadata.pictures)
        self.assertEqual(cleaned.applications, metadata.applications)


class M4AMetaDataTest(MetaDataTest):
    def setUp(self):
        self.metadata_class = audiotools.M4AMetaData
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "composer_name",
                                 "copyright",
                                 "year",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = [audiotools.M4AAudio,
                                  audiotools.ALACAudio]

    def empty_metadata(self):
        return self.metadata_class.converted(audiotools.MetaData())

    @METADATA_M4A
    def test_foreign_field(self):
        metadata = audiotools.M4AMetaData([])
        metadata["\xa9nam"] = audiotools.M4AMetaData.text_atom(
            "\xa9nam", u'Track Name')
        metadata["\xa9alb"] = audiotools.M4AMetaData.text_atom(
            "\xa9alb", u'Album Name')
        metadata["trkn"] = audiotools.M4AMetaData.trkn_atom(
            1, 3)
        metadata["disk"] = audiotools.M4AMetaData.disk_atom(
            2, 4)
        metadata["\xa9foo"] = audiotools.M4AMetaData.text_atom(
            "\xa9foo", u'Bar')
        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name,
                                        BLANK_PCM_Reader(1))
                track.set_metadata(metadata)
                metadata2 = track.get_metadata()
                self.assertEqual(metadata, metadata2)
                self.assertEqual(metadata.__class__, metadata2.__class__)
                self.assertEqual(unicode(track.get_metadata()["\xa9foo"][0]),
                                 u"Bar")
            finally:
                temp_file.close()

    @METADATA_M4A
    def test_field_mapping(self):
        mapping = [('track_name', '\xA9nam', u'a'),
                   ('artist_name', '\xA9ART', u'b'),
                   ('year', '\xA9day', u'c'),
                   ('album_name', '\xA9alb', u'd'),
                   ('composer_name', '\xA9wrt', u'e'),
                   ('comment', '\xA9cmt', u'f'),
                   ('copyright', 'cprt', u'g')]

        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name, BLANK_PCM_Reader(1))

                #ensure that setting a class field
                #updates its corresponding low-level implementation
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    setattr(metadata, field, value)
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(unicode(metadata[key][0]),
                                     unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata2, field), value)
                    self.assertEqual(unicode(metadata2[key][0]),
                                     unicode(value))

                #ensure that updating the low-level implementation
                #is reflected in the class field
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    metadata[key] = audiotools.M4AMetaData.text_atom(
                        key, unicode(value))
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(unicode(metadata[key][0]),
                                     unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(unicode(metadata[key][0]),
                                     unicode(value))

                #ensure that setting numerical fields also
                #updates the low-level implementation
                track.delete_metadata()
                metadata = self.empty_metadata()
                metadata.track_number = 1
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['trkn'][0]),
                                 u'1')
                metadata.track_total = 2
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['trkn'][0]),
                                 u'1/2')
                del(metadata.track_number)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['trkn'][0]),
                                 u'0/2')
                del(metadata.track_total)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertRaises(KeyError,
                                  metadata.__getitem__,
                                  'trkn')

                track.delete_metadata()
                metadata = self.empty_metadata()
                metadata.album_number = 3
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['disk'][0]),
                                 u'3')
                metadata.album_total = 4
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['disk'][0]),
                                 u'3/4')
                del(metadata.album_number)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(unicode(metadata['disk'][0]),
                                 u'0/4')
                del(metadata.album_total)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertRaises(KeyError,
                                  metadata.__getitem__,
                                  'disk')
            finally:
                temp_file.close()

    @METADATA_M4A
    def test_images(self):
        for audio_class in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_class.SUFFIX)
            try:
                track = audio_class.from_pcm(temp_file.name,
                                             BLANK_PCM_Reader(1))

                metadata = self.empty_metadata()
                self.assertEqual(metadata.images(), [])

                image1 = audiotools.Image.new(TEST_COVER1, u"", 0)

                track.set_metadata(metadata)
                metadata = track.get_metadata()

                #ensure that adding one image works
                metadata.add_image(image1)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.images(), [image1])

                #ensure that deleting the first image works
                metadata.delete_image(image1)
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata.images(), [])

            finally:
                temp_file.close()

    @METADATA_M4A
    def test_converted(self):
        #build a generic MetaData with everything
        image1 = audiotools.Image.new(TEST_COVER1, "", 0)

        metadata_orig = audiotools.MetaData(track_name=u"a",
                                            track_number=1,
                                            track_total=2,
                                            album_name=u"b",
                                            artist_name=u"c",
                                            performer_name=u"d",
                                            composer_name=u"e",
                                            conductor_name=u"f",
                                            media=u"g",
                                            ISRC=u"h",
                                            catalog=u"i",
                                            copyright=u"j",
                                            publisher=u"k",
                                            year=u"l",
                                            date=u"m",
                                            album_number=3,
                                            album_total=4,
                                            comment="n",
                                            images=[image1])

        #ensure converted() builds something with our class
        metadata_new = self.metadata_class.converted(metadata_orig)
        self.assertEqual(metadata_new.__class__, self.metadata_class)

        #ensure our fields match
        for field in audiotools.MetaData.__FIELDS__:
            if (field in self.supported_fields):
                self.assertEqual(getattr(metadata_orig, field),
                                 getattr(metadata_new, field))
            elif (field in audiotools.MetaData.__INTEGER_FIELDS__):
                self.assertEqual(getattr(metadata_new, field), 0)
            else:
                self.assertEqual(getattr(metadata_new, field), u"")

        #ensure images match, if supported
        if (self.metadata_class.supports_images()):
            self.assertEqual(metadata_new.images(), [image1])

        #check non-MetaData fields
        metadata_orig = self.empty_metadata()
        metadata_orig['test'] = audiotools.M4AMetaData.binary_atom(
            'test', "foobar")
        self.assertEqual(metadata_orig['test'][0].data[0].data, "foobar")
        metadata_new = self.metadata_class.converted(metadata_orig)
        self.assertEqual(metadata_new['test'][0].data[0].data, "foobar")

    @METADATA_M4A
    def test_clean(self):
        #check trailing whitespace
        metadata = audiotools.M4AMetaData([])
        metadata["\xa9nam"] = audiotools.M4AMetaData.text_atom(
            "\xa9nam", u'Foo ')
        self.assertEqual(unicode(metadata["\xa9nam"][0]), u'Foo ')
        self.assertEqual(metadata.track_name, u'Foo ')
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_("removed trailing whitespace from %(field)s") %
                          {"field":"nam"}])
        self.assertEqual(unicode(cleaned["\xa9nam"][0]), u'Foo')
        self.assertEqual(cleaned.track_name, u'Foo')

        #check leading whitespace
        metadata = audiotools.M4AMetaData([])
        metadata["\xa9nam"] = audiotools.M4AMetaData.text_atom(
            "\xa9nam", u' Foo')
        self.assertEqual(unicode(metadata["\xa9nam"][0]), u' Foo')
        self.assertEqual(metadata.track_name, u' Foo')
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_("removed leading whitespace from %(field)s") %
                          {"field":"nam"}])
        self.assertEqual(unicode(cleaned["\xa9nam"][0]), u'Foo')
        self.assertEqual(cleaned.track_name, u'Foo')

        #check empty fields
        metadata = audiotools.M4AMetaData([])
        metadata["\xa9nam"] = audiotools.M4AMetaData.text_atom(
            "\xa9nam", u'')
        self.assertEqual(unicode(metadata["\xa9nam"][0]), u'')
        self.assertEqual(metadata.track_name, u'')
        fixes = []
        cleaned = metadata.clean(fixes)
        self.assertEqual(fixes,
                         [_("removed empty field %(field)s") %
                          {"field":"nam"}])
        self.assertRaises(KeyError,
                          cleaned.__getitem__,
                          '\xa9nam')
        self.assertEqual(cleaned.track_name, u'')

        #numerical fields can't have whitespace
        #and images aren't stored with metadata
        #so there's no need to check those


class VorbisCommentTest(MetaDataTest):
    def setUp(self):
        self.metadata_class = audiotools.VorbisComment
        self.supported_fields = ["track_name",
                                 "track_number",
                                 "track_total",
                                 "album_name",
                                 "artist_name",
                                 "performer_name",
                                 "composer_name",
                                 "conductor_name",
                                 "media",
                                 "ISRC",
                                 "catalog",
                                 "copyright",
                                 "publisher",
                                 "year",
                                 "album_number",
                                 "album_total",
                                 "comment"]
        self.supported_formats = [audiotools.VorbisAudio,
                                  audiotools.SpeexAudio]

    def empty_metadata(self):
        return self.metadata_class.converted(audiotools.MetaData())

    @METADATA_VORBIS
    def test_foreign_field(self):
        metadata = audiotools.VorbisComment(
            {"TITLE": [u'Track Name'],
             "ALBUM": [u'Album Name'],
             "TRACKNUMBER": [u"1"],
             "TRACKTOTAL": [u"3"],
             "DISCNUMBER": [u"2"],
             "DISCTOTAL": [u"4"],
             "FOO": [u"Bar"]})
        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name,
                                        BLANK_PCM_Reader(1))
                track.set_metadata(metadata)
                metadata2 = track.get_metadata()
                self.assertEqual(metadata, metadata2)
                self.assertEqual(metadata.__class__, metadata2.__class__)
                self.assertEqual(metadata2["FOO"], [u"Bar"])
            finally:
                temp_file.close()

    @METADATA_VORBIS
    def test_field_mapping(self):
        mapping = [('track_name', 'TITLE', u'a'),
                   ('track_number', 'TRACKNUMBER', 1),
                   ('track_total', 'TRACKTOTAL', 2),
                   ('album_name', 'ALBUM', u'b'),
                   ('artist_name', 'ARTIST', u'c'),
                   ('performer_name', 'PERFORMER', u'd'),
                   ('composer_name', 'COMPOSER', u'e'),
                   ('conductor_name', 'CONDUCTOR', u'f'),
                   ('media', 'SOURCE MEDIUM', u'g'),
                   ('ISRC', 'ISRC', u'h'),
                   ('catalog', 'CATALOG', u'i'),
                   ('copyright', 'COPYRIGHT', u'j'),
                   ('year', 'DATE', u'k'),
                   ('album_number', 'DISCNUMBER', 3),
                   ('album_total', 'DISCTOTAL', 4),
                   ('comment', 'COMMENT', u'l')]

        for format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(suffix="." + format.SUFFIX)
            try:
                track = format.from_pcm(temp_file.name, BLANK_PCM_Reader(1))

                #ensure that setting a class field
                #updates its corresponding low-level implementation
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    setattr(metadata, field, value)
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(
                        metadata[key][0],
                        unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata2, field), value)
                    self.assertEqual(
                        metadata2[key][0],
                        unicode(value))

                #ensure that updating the low-level implementation
                #is reflected in the class field
                for (field, key, value) in mapping:
                    track.delete_metadata()
                    metadata = self.empty_metadata()
                    metadata[key] = [unicode(value)]
                    self.assertEqual(getattr(metadata, field), value)
                    self.assertEqual(
                        metadata[key][0],
                        unicode(value))
                    track.set_metadata(metadata)
                    metadata2 = track.get_metadata()
                    self.assertEqual(getattr(metadata2, field), value)
                    self.assertEqual(
                        metadata2[key][0],
                        unicode(value))
            finally:
                temp_file.close()

    @METADATA_VORBIS
    def test_supports_images(self):
        self.assertEqual(self.metadata_class.supports_images(), False)

    @METADATA_VORBIS
    def test_lowercase(self):
        for audio_format in self.supported_formats:
            temp_file = tempfile.NamedTemporaryFile(
                suffix="." + audio_format.SUFFIX)
            try:
                track = audio_format.from_pcm(temp_file.name,
                                              BLANK_PCM_Reader(1))

                lc_metadata = audiotools.VorbisComment(
                        {"title": [u"track name"],
                         "tracknumber": [u"1"],
                         "tracktotal": [u"3"],
                         "album": [u"album name"],
                         "artist": [u"artist name"],
                         "performer": [u"performer name"],
                         "composer": [u"composer name"],
                         "conductor": [u"conductor name"],
                         "source medium": [u"media"],
                         "isrc": [u"isrc"],
                         "catalog": [u"catalog"],
                         "copyright": [u"copyright"],
                         "publisher": [u"publisher"],
                         "date": [u"2009"],
                         "discnumber": [u"2"],
                         "disctotal": [u"4"],
                         "comment": [u"some comment"]},
                        u"vendor string")

                metadata = audiotools.MetaData(
                    track_name=u"track name",
                    track_number=1,
                    track_total=3,
                    album_name=u"album name",
                    artist_name=u"artist name",
                    performer_name=u"performer name",
                    composer_name=u"composer name",
                    conductor_name=u"conductor name",
                    media=u"media",
                    ISRC=u"isrc",
                    catalog=u"catalog",
                    copyright=u"copyright",
                    publisher=u"publisher",
                    year=u"2009",
                    album_number=2,
                    album_total=4,
                    comment=u"some comment")

                track.set_metadata(lc_metadata)
                track = audiotools.open(track.filename)
                self.assertEqual(metadata, lc_metadata)

                track = audio_format.from_pcm(temp_file.name,
                                              BLANK_PCM_Reader(1))
                track.set_metadata(audiotools.MetaData(
                        track_name=u"Track Name",
                        track_number=1))
                metadata = track.get_metadata()
                self.assertEqual(metadata["TITLE"], [u"Track Name"])
                self.assertEqual(metadata["TRACKNUMBER"], [u"1"])
                self.assertEqual(metadata.track_name, u"Track Name")
                self.assertEqual(metadata.track_number, 1)

                metadata["title"] = [u"New Track Name"]
                metadata["tracknumber"] = [u"2"]
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata["TITLE"], [u"New Track Name"])
                self.assertEqual(metadata["TRACKNUMBER"], [u"2"])
                self.assertEqual(metadata.track_name, u"New Track Name")
                self.assertEqual(metadata.track_number, 2)

                metadata.track_name = "New Track Name 2"
                metadata.track_number = 3
                track.set_metadata(metadata)
                metadata = track.get_metadata()
                self.assertEqual(metadata["TITLE"], [u"New Track Name 2"])
                self.assertEqual(metadata["TRACKNUMBER"], [u"3"])
                self.assertEqual(metadata.track_name, u"New Track Name 2")
                self.assertEqual(metadata.track_number, 3)
            finally:
                temp_file.close()

    @METADATA_VORBIS
    def test_totals(self):
        metadata = self.empty_metadata()
        metadata["TRACKNUMBER"] = [u"2/4"]
        self.assertEqual(metadata.track_number, 2)
        self.assertEqual(metadata.track_total, 4)

        metadata = self.empty_metadata()
        metadata["DISCNUMBER"] = [u"1/3"]
        self.assertEqual(metadata.album_number, 1)
        self.assertEqual(metadata.album_total, 3)

    @METADATA_VORBIS
    def test_clean(self):
        #check trailing whitespace
        metadata = audiotools.VorbisComment({"TITLE":[u"Foo "]},
                                            u"vendor")
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned,
                         audiotools.VorbisComment({"TITLE":[u"Foo"]},
                                                  u"vendor"))
        self.assertEqual(results,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TITLE"}])

        #check leading whitespace
        metadata = audiotools.VorbisComment({"TITLE":[u" Foo"]},
                                            u"vendor")
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned,
                         audiotools.VorbisComment({"TITLE":[u"Foo"]},
                                                  u"vendor"))
        self.assertEqual(results,
                         [_(u"removed leading whitespace from %(field)s") %
                          {"field":u"TITLE"}])

        #check leading zeroes
        metadata = audiotools.VorbisComment({"TRACKNUMBER":[u"001"]},
                                            u"vendor")
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned,
                         audiotools.VorbisComment({"TRACKNUMBER":[u"1"]},
                                                  u"vendor"))
        self.assertEqual(results,
                         [_(u"removed leading zeroes from %(field)s") %
                          {"field":u"TRACKNUMBER"}])

        #check empty fields
        metadata = audiotools.VorbisComment({"TITLE":[u""]},
                                            u"vendor")
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned,
                         audiotools.VorbisComment({}, u"vendor"))
        self.assertEqual(results,
                         [_(u"removed empty field %(field)s") %
                          {"field":u"TITLE"}])

        metadata = audiotools.VorbisComment({"TITLE":[u"    "]},
                                            u"vendor")
        results = []
        cleaned = metadata.clean(results)
        self.assertEqual(cleaned,
                         audiotools.VorbisComment({}, u"vendor"))
        self.assertEqual(results,
                         [_(u"removed trailing whitespace from %(field)s") %
                          {"field":u"TITLE"},
                          _(u"removed empty field %(field)s") %
                          {"field":u"TITLE"}])
