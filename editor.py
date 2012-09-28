#!/usr/bin/env python

class Editor(object):
    """
    Editor object to replay editing sessions

    all edit operations return new cursor position
    """

    def __init__(self, text=None):
        self.text = []
        if text:
            self.text = list(text)
    
    def __str__(self):
        return "".join(self.text)

    def __len__(self):
        return len(self.text)

    def insert(self, pos, chars):
        assert pos <= len(self)
        for c in chars:
            self.text.insert(pos, c)
            pos += 1
        return pos

    def delete(self, pos, chars=None):
        n_deleted = 1
        if chars:
            n_deleted = len(chars)
        for i in range(n_deleted):
            c = self.text.pop(pos)
            if chars:
                assert c == chars[i], "expected char '%s' at pos %s of '%s' but found '%s'" %(chars[i], pos, str(self), c)
        return pos

    def backspace(self, pos, chars=None):
        n_deleted = 1
        if chars:
            n_deleted = len(chars)
        for i in range(n_deleted):
            # backspace = move cursor to left and delete one character
            pos -= 1
            pos = self.delete(pos, chars[i])
        return pos

if __name__ == '__main__':
    e = Editor("")
    e.insert(0, 'Haus')   # 'Haus'
    e.insert(0, 'Mein ')  # 'Mein Haus'
    e.insert(5, 'kleines ') # 'Mein kleines Haus'
    e.delete(0)             # 'ein kleines Haus'
    e.delete(4, 'kleines')  # 'ein  Haus'
    e.delete(4)             # 'ein Haus'


    print e
