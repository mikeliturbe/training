import textwrap
import time

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from app.utility.base_service import BaseService
from app.utility.payload_encoder import xor_file
from plugins.training.app.encoder import Encoder
from plugins.training.app.obfuscator import A
from plugins.training.app.utility.block import BlockChain


class TrainingService(BaseService):

    def __init__(self, services):
        self.log = self.add_service('training_svc', self)
        self.data_svc = services.get('data_svc')
        self.certify_key = dict()
        self.blockchain = BlockChain()
        self.blockchain.create_genesis_block()
        self.encoder = Encoder()
        self.services = services
        self._text = dict(font='Verdana.ttf', version_txt_size=48, cert_txt_size=150,
                          name_txt_size=100, color='white', max_name_txt_char_len=24,
                          max_cert_name_txt_char_len=15)

    async def load_key_for_existing_solves(self):
        try:
            flags, badges = await self.get_all_flags_and_badges()
            for badge in badges:
                for flag in badge.flags:
                    if await flag.verify(self.services):
                        await self.update_blockchain(badge, flag)
        except Exception as e:
            print(e)

    async def get_all_flags_and_badges(self, data=None):
        badges = [badge for c in await self.data_svc.locate('certifications', data) for badge in c.badges]
        return [flag for b in badges for flag in b.flags], badges

    async def build_certificate(self, name, cert_name):
        buff = xor_file(input_file=self.encoder.encoded_cert_path,
                        key=[ord(elem) for v in self.certify_key.values() for elem in v])
        return await self._populate_cert(name, buff, cert_name)

    async def update_blockchain(self, badge, flag):
        self.blockchain.add_new_transaction(dict(timestamp=time.time(),
                                                 flag_name=flag.name,
                                                 completed=await flag.verify(self.services)))
        self.blockchain.mine()
        self.certify_key['%s-%s' % (badge.name, flag.number)] = await A(flag, self.blockchain, BlockChain)
        flag.completed = True

    """ PRIVATE """

    async def _populate_cert(self, name, buff, cert_name):
        return await self._render_cert_text(buff=buff, name=await self._wrap_text(name=name,
                                                                                  field='max_name_txt_char_len'),
                                            cert_name=await self._wrap_text(name=cert_name,
                                                                            field='max_cert_name_txt_char_len'))

    async def _wrap_text(self, name, field):
        return '\n'.join(textwrap.TextWrapper(width=self._text[field]).wrap(text=name))

    async def _render_cert_text(self, buff, name, cert_name):
        try:
            im = Image.open(BytesIO(buff))
            draw = ImageDraw.Draw(im)
            name_font = ImageFont.truetype(self._text['font'], self._text['name_txt_size'])
            version_font = ImageFont.truetype(self._text['font'], self._text['version_txt_size'])
            cert_font = ImageFont.truetype(self._text['font'], self._text['cert_txt_size'])
            draw.text((1000, 1200), name, font=name_font, fill=self._text['color'])
            draw.text((1625, 260), 'v.2.6.4', font=version_font, fill=self._text['color'])
            draw.text((220, 250), cert_name, font=cert_font, fill=self._text['color'])
            out_buff = BytesIO()
            im.save(out_buff, format='JPEG')
            return out_buff.getvalue()
        except Exception as e:
            print(e)
