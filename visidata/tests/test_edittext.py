# Copyright (C) 2016 Paul Watts
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from unittest import skip
from unittest.mock import Mock, patch

from visidata.tui import editText, EscapeException, Key, Ctrl, DEL

class EditTextTestCase(unittest.TestCase):
    def setUp(self):
        self.scr = Mock()
        self.scr.addstr = Mock()
        self.scr.move = Mock()
        self.chars=[]
        self.scr.getch = Mock(side_effect=self.chars)

    def mock_getch(self, *chars):
        self.chars.extend(chars)

    def t(self, *keys, result=None, exception=None, **kwargs):
        for k in keys:
            if isinstance(k, str):
                for ch in k:
                    self.mock_getch(ord(ch))
            else:
                self.mock_getch(k)
        if exception:
            with self.assertRaises(exception):
                editText(self.scr, 0, 0, 0, **kwargs)
        else:
            r = editText(self.scr, 0, 0, 0, **kwargs)
            self.assertEqual(r, result)

    def tests(self):
        self.t(Key.ENTER, result='')
        self.t(Key.IC, 'ab', Key.HOME, 'cd', Ctrl.A, 'ef', Key.ENTER, result='efcdab')
        self.t(Key.IC, 'ab', Key.LEFT, '1', Key.LEFT, Key.LEFT, Key.LEFT, '2', Key.ENTER, result='2a1b') # Left, past home
        self.t(Key.IC, 'ab', Ctrl.C, exception=EscapeException)
        self.t(Key.IC, 'ab', Key.ESC, exception=EscapeException)
        self.t(Key.IC, 'a', Key.DC, Key.ENTER, result='a')
        self.t(Key.IC, 'ab', Key.LEFT, Key.DC, Key.ENTER, result='a')
        self.t(Key.IC, 'ab', Key.LEFT, 'c', Key.END, 'd', Key.ENTER, result='acbd')
        self.t(Key.IC, 'ab', Key.HOME, Key.RIGHT, 'c', Key.ENTER, result='acb')
        self.t(Key.IC, 'ab', Key.BACKSPACE, 'c', Key.ENTER, result='ac')

        # Backspace deletes the first character at the start
        self.t(Key.IC, 'ab', Key.HOME, Key.BACKSPACE, 'c', Key.ENTER, result='cb')

        # Backspace works in different combos, including on the mac.
        self.t('abc', Key.BACKSPACE, Ctrl.H, DEL, Key.ENTER, result='')

        # ^J works the same way as ENTER.
        self.t('abc', Ctrl.J, result='abc')

        self.t('abc', Ctrl.B, Ctrl.B, Ctrl.K, Key.ENTER, result='a')

        self.t('a', Ctrl.R, Key.ENTER, result='')
        self.t('a', Ctrl.R, Key.ENTER, value='foo', result='foo')

        # With one character is a no-op
        #self.t('a', Ctrl.T, Key.ENTER, result='a')

        # Two characters swaps characters
        self.t('ab', Ctrl.T, Key.ENTER, result='ba')

        # Home with multiple characters acts like delete
        self.t('ab', Key.HOME, Ctrl.T, Key.ENTER, result='b')

        #self.t(Ctrl.T, Key.ENTER, result='')
        self.t('ab', Key.LEFT, Ctrl.U, Key.ENTER, result='b')
        self.t('ab', Ctrl.U, 'c', Key.ENTER, result='c')

    # TODO: Test ctrl-V. What does it do?
    # TODO: Test value
    # TODO: Test fillchar
