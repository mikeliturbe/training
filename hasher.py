import hashlib
import stepic

from PIL import Image
from importlib import import_module
from dill.source import getsource

from app.utility.base_world import BaseWorld

super_secret_hash = ''
chosen_hash = hashlib.sha512()
cert = BaseWorld.strip_yml('plugins/training/data/9cd5f3a0-765d-45bc-85c2-bc76d4282599.yml')[0]
for badge, flags in cert['badges'].items():
    for flag in flags['flags']:
        flag_module = import_module('plugins.training.app.%s' % flag)
        flag_verify = getattr(flag_module, 'verify')
        chosen_hash.update(getsource(flag_verify).encode())
        super_secret_hash += chosen_hash.hexdigest()

with open('plugins/training/app/c_flag.py', 'r') as c_flag:
    chosen_hash.update(c_flag.read().encode())
    super_secret_hash += chosen_hash.hexdigest()

print(super_secret_hash)
im = Image.open('static/img/duk.png')
im1 = stepic.encode(im, super_secret_hash.encode())
im1.save('static/img/duk.png', 'PNG')

im2 = Image.open('duk.png')
stegoImage = stepic.decode(im2)
print(stegoImage)
