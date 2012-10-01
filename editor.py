#!/usr/bin/env python

class EditException(Exception):
    def __init__(self, value):
        self.message = value
    def __str__(self):
        return self.message

class SeriousEditException(Exception):
    def __init__(self, value):
        self.message = value
    def __str__(self):
        return self.message

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

    def check_delete(self, pos, expected_chars):
        #if pos + len(expected_chars) > len(self.text):
        #    return False
        for i, c_expected in enumerate(expected_chars):
            if not self.text[pos+i] == c_expected:
                return False
        return True

    def check_backspace(self, pos, expected_chars):
        new_pos = pos - len(expected_chars) + 1
        return self.check_delete(new_pos, expected_chars)

    def delete(self, pos, chars=None):
        n_deleted = 1
        if chars:
            n_deleted = len(chars)
        for i in range(n_deleted):
            if chars:
                c = self.text[pos]
                if c != chars[i]:
                    print list(enumerate(self.text))
                    message = "expected char '%s' at pos %s of '%s' but found '%s'\n" %(chars[i], pos, str(self), c)
                    raise SeriousEditException(message)
                assert c == chars[i]
            self.text.pop(pos)
        return pos

    def backspace(self, pos, chars):
        new_pos = pos - len(chars) + 1
        print new_pos, chars
        pos = self.delete(new_pos, chars)
        return pos

        #n_deleted = 1
        #if chars:
        #    n_deleted = len(chars)
        #for i in range(n_deleted):
        #    # backspace = move cursor to left and delete one character
        #    pos -= 1
        #    pos = self.delete(pos, chars[i])
        #return pos

if __name__ == '__main__':
    e = Editor("")
    e.insert(0, 'Haus')   # 'Haus'
    e.insert(0, 'Mein ')  # 'Mein Haus'
    e.insert(5, 'kleines ') # 'Mein kleines Haus'
    e.delete(0)             # 'ein kleines Haus'
    print e.check_delete(4, 'kleines')
    print e.check_backspace(4, 'kleines')
    print e.check_backspace(10, 'kleines')
    e.delete(4, 'kleines')  # 'ein  Haus'
    e.delete(4)             # 'ein Haus'


    print e
