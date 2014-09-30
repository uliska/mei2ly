#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           ly2mei
# Program Description:    Convert LilyPond source files to MEI.
#
# Filename:               __main__.py
# Purpose:                Run the program.
#
# Copyright (C) 2014 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>

Convert LilyPond source files to MEI. This is the main entry point.

At the moment, this file works on a series of space-separated notes---nothing else. For example, the
following LilyPond markup:::

    a4( b'16 c,,2)

produces something like this MEI markup:::

    <layer>
        <note dur="4" oct="3" pname="A" slur="i1" xml:id="4da1e537" />
        <note dur="16" oct="4" pname="B" xml:id="839fecca" />
        <note dur="2" oct="1" pname="C" slur="t1" xml:id="d4f1fda1" />
        <slur startid="#4da1e537" endid="#d4f1fda1" plist="#4da1e537 #839fecca #d4f1fda1"/>
    </layer>

Syntax Whitelist
===========================
This is a list of the currently-allowed syntax. If something does not appear on this list, it is
not picked up by the ``ly2mei`` program. The ``sillytest.ly`` file should use all the features at
least once.

    - [a..g] letter names for pitch (i.e., do not use accidentals or rests)
    - absolute octave entry (i.e., do not use ``\relative``)
    - durations specified on every note including 1, 2, 4, 8, 16, 32, 64, ... (not ``\longa`` etc.
        or dotted durations)
    - slurs *within a single measure*
    - multiple measures separated by ``|`` (including trailing bar-check)
"""

import six
from six.moves import range

import sys
import uuid
from lxml import etree as ETree


_XMLNS = '{http://www.w3.org/XML/1998/namespace}'
_XMLID = '{http://www.w3.org/XML/1998/namespace}id'
_MEINS = '{http://www.music-encoding.org/ns/mei}'

_VALID_NOTE_LETTERS = ('a', 'b', 'c', 'd', 'e', 'f', 'g')


# register the 'mei' namespace
ETree.register_namespace('mei', _MEINS[1:-1])


def find_lowest_of(here, these):
    """
    Finds the lowest (left-most) offset at which any of ``these`` appears in ``here``.

    **Examples**

    >>> find_lowest_of('hollaback', ['a', 'b', 'c'])
    4
    """
    for i, letter in enumerate(here):
        if letter in these:
            return i


def do_pitch_class(markup):
    """
    Given the part of a LilyPond note that includes the pitch class specification, find it. Rests
    and spacers also work, but note the return type below.

    :returns: Eiether a tuple indicating the required values for the @pname and @accid attributes,
        respectively, or a single string indicating what type of rest or space object this is.
    :rtype: 2-tuple of str or str

    **Examples**

    Usual pitch classes:

    >>> do_pitch_class('f')
    ('F', None)
    >>> do_pitch_class('fis')
    ('F', 's')
    >>> do_pitch_class('deses')
    ('D', 'ff')
    >>> do_pitch_class('es')
    ('E', 'f')

    Rests and spacers:

    >>> do_pitch_class('r')
    'rest'
    >>> do_pitch_class('R')
    'REST'
    >>> do_pitch_class('s')
    'space'
    """
    # TODO: rewrite this silly function

    if 1 == len(markup):
        if markup in _VALID_NOTE_LETTERS:
            return markup.upper(), None
        elif 'r' == markup:
            return 'rest'
        elif 'R' == markup:
            return 'rest'
        elif 's' == markup:
            return 'space'
        else:
            pass  # TODO: panic?
    else:
        letter = do_pitch_class(markup[0])[0]
        accid = markup[1:]
        if 's' == accid and ('a' == letter or 'e' == letter):
            return letter, 's'
        elif 0 != len(accid) % 2:
            pass  # TODO: panic?
        else:
            if 'is' == accid:
                return letter, 's'
            elif 'es' == accid:
                return letter, 'f'
            elif 'isis' == accid:
                return letter, 'ss'
            elif 'eses' == accid:
                return letter, 'ff'
            else:
                pass  # TODO: panic?


def do_note_block(markup):
    """
    Convert a "block" with a note and its related objects (articulations, dynamics, etc.).

    .. note:: You can figure out what to do for slurs based on the @slur attribute. If it's ``'i1'``
        or ``'t1'`` that means to start or end a slur, respectively. If it's ``'i2'`` or ``'t2'``
        it's for a phrasing slur.
    """
    # figure out @pname and @accid
    pname, accid = do_pitch_class(markup[:find_lowest_of(markup, [',', "'", '1', '2', '4', '8'])])

    octave = 3
    stopped_at = 0

    # figure out @oct
    for i in range(1, len(markup)):
        each_char = markup[i]
        if each_char.isdigit():
            stopped_at = i
            break
        elif ',' == each_char:
            octave -= 1
        else:  # assume it's '
            octave += 1

    # figure out @dur
    dur = ''
    for i in range(stopped_at, len(markup)):
        each_char = markup[i]
        if each_char.isdigit():
            dur += each_char
        else:
            stopped_at = i
            break

    the_elem = ETree.Element('{}note'.format(_MEINS),
                             {'pname': pname, 'dur': dur, 'oct': str(octave),
                              _XMLID: str(uuid.uuid4())})
    if accid is not None:
        the_elem.set('accid', accid)

    # figure out a slur
    if '(' in markup:
        the_elem.set('slur', 'i1')
    elif ')' in markup:
        the_elem.set('slur', 't1')

    return the_elem


def do_measure(markup):
    """
    Process all the stuff in a single measure.

    (This is for a LilyPond measure, where there may be multiple voices, but [normally!] one staff).
    """
    list_of_elems = []
    slur_active = None
    for each_note in markup.split():
        elem = do_note_block(each_note)
        list_of_elems.append(elem)

        if 'i1' == elem.get('slur'):
            if slur_active is not None:
                pass  # TODO: should panic; this means a slur wasn't closed
            else:
                slur_active = ETree.Element('{}slur'.format(_MEINS),
                                            {'startid': elem.get(_XMLID),
                                             _XMLID: str(uuid.uuid4())})
        elif 't1' == elem.get('slur'.format(_MEINS)):
            slur_active.set('endid', elem.get(_XMLID))
            list_of_elems.append(slur_active)
            slur_active = None

    if 0 == len(list_of_elems):
        # if the measure was somehow empty
        return None

    # NOTE: this is a bit of a lie for now, just to make it work
    # TODO: adjust @n for the voice number
    layer = ETree.Element('{}layer'.format(_MEINS), {'n': '1', _XMLID: str(uuid.uuid4())})
    [layer.append(x) for x in list_of_elems]
    staff = ETree.Element('{}staff'.format(_MEINS), {'n': '1', _XMLID: str(uuid.uuid4())})
    staff.append(layer)
    measure = ETree.Element('{}measure'.format(_MEINS), {_XMLID: str(uuid.uuid4())})
    measure.append(staff)

    return measure


if '__main__' == __name__:
    try:
        with open(sys.argv[1], 'r') as the_file:
            # NOTE: this isn't good because an enormous file might overwhelm the computer's
            # available memory. But it works for now, when I'm not trying to fy my own computer.
            source = the_file.read()
    except IOError:
        print('There was an IOError while reading the source file.')
        sys.exit(1)

    measures = []
    for i, each_measure in enumerate(source.split('|')):
        elem = do_measure(each_measure)
        if elem is not None:
            elem.set('n', str(i + 1))
            measures.append(elem)

    # falsify everything into a valid structure
    section = ETree.Element('{}section'.format(_MEINS))
    [section.append(x) for x in measures]
    score = ETree.Element('{}score'.format(_MEINS))
    score.append(section)
    body = ETree.Element('{}body'.format(_MEINS))
    body.append(score)
    music = ETree.Element('{}music'.format(_MEINS))
    music.append(body)
    mei_elem = ETree.Element('{}mei'.format(_MEINS), {'meiversion': '2013'})
    mei_elem.append(music)

    print('here it is!\n')
    ETree.dump(mei_elem)

    print('\noutputting!\n')
    whole_doc = ETree.ElementTree(mei_elem)
    whole_doc.write('test_file.mei',
                    encoding='UTF-8',
                    xml_declaration=True,
                    pretty_print=True)