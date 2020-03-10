import hashlib

from app.utility.base_object import BaseObject


class Badge(BaseObject):

    @property
    def key(self):
        key = ''
        chosen_hash = hashlib.md5()
        for flag in self.flags:
            chosen_hash.update(str(flag).encode())
            key += chosen_hash.hexdigest()
        return key

    @property
    def unique(self):
        return self.hash('%s' % self.name)

    @property
    def display(self):
        return dict(name=self.name, flags=[f.display for f in self.flags], verify=False)

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.flags = []
