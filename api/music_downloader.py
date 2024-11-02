import os
import re
import base64
import requests
import json
from lxml import etree
from Crypto.Cipher import AES


class MusicDownloader:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }
        # self.playlist_url_temp = 'http://music.163.com/playlist?id={}'  # 歌单页面真实url,填充歌单的id,从用户传来的链接中提取
        # self.album_url_temp = 'http://music.163.com/album?id={}'  # 专辑真实url,填充专辑id
        # self.song_url_temp = 'http://music.163.com/song?id={}'  # 单曲真实url

        self.second_param = "010001"  # 不可变
        # 不可变
        self.third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.forth_param = "0CoJUm6Qyw8W8jud"  # 不可变
        self.song_url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
    def parse_url(self, url):
        resp = requests.get(url, headers=self.headers)
        return resp.content

    def get_song_id_name(self, resp):
        resp = resp.decode()
        html_ele = etree.HTML(resp)
        a_list = html_ele.xpath('//div[@id="song-list-pre-cache"]//a')
        if a_list:
            content_list = []
            for a in a_list:
                song_name = a.xpath('./text()')[0] if a.xpath('./text()') else None
                song_id = a.xpath('./@href')[0] if a.xpath('./@href') else None
                if song_id:
                    ret = re.match(r'/song\?id=(\d+)', song_id)
                    song_id = ret.group(1) if ret else None
                content_list.append((song_name, song_id))
            return content_list
        return []

    def get_params(self, song_id):
        iv = "0102030405060708"
        first_key = self.forth_param
        second_key = 16 * 'F'
        first_param = "{\"ids\":\"[" + song_id + "]\",\"br\":128000,\"csrf_token\":\"\"}"
        h_encText = self.AES_encrypt(first_param, first_key, iv)
        h_encText = self.AES_encrypt(h_encText.decode('utf-8'), second_key, iv)
        return h_encText.decode('utf-8')

    def get_encSecKey(self):
        encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
        return encSecKey

    def AES_encrypt(self, text, key, iv):
        text = text.encode('utf-8')
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad).encode('utf-8')
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text

    def get_json(self, params, encSecKey):
        data = {
            "params": params,
            "encSecKey": encSecKey
        }
        response = requests.post(self.song_url, headers=self.headers, data=data)
        return response.content.decode()

    def get_song_content(self, song_id):
        params = self.get_params(song_id)
        encSecKey = self.get_encSecKey()
        json_text = self.get_json(params, encSecKey)
        json_dict = json.loads(json_text)
        song_real_url = json_dict.get('data')[0].get('url')
        music_format = json_dict.get('data')[0].get('type')
        try:
            song_content = self.parse_url(song_real_url)  # 得到歌曲二进制数据
        except Exception as e:
            print(f"解析URL时出错: {e}")
            print("无法获取歌曲的内容，大概率权限不足")
        return song_content, music_format

    def save_song(self, song_name, music_format, song_content, filepath):
        print(song_name, '开始下载')
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(os.path.join(filepath, f'{song_name}.{music_format}'), 'wb') as f:
            f.write(song_content)
        print(song_name, '下载完成')

    def download_playlist(self, playlist_url, filepath):
        resp = self.parse_url(playlist_url)
        song_id_name = self.get_song_id_name(resp)
        for song_name, song_id in song_id_name:
            song_content, music_format = self.get_song_content(song_id)
            self.save_song(song_name, music_format, song_content, filepath)

    def download_album(self, album_url, filepath):
        resp = self.parse_url(album_url)
        song_id_name = self.get_song_id_name(resp)
        for song_name, song_id in song_id_name:
            song_content, music_format = self.get_song_content(song_id)
            self.save_song(song_name, music_format, song_content, filepath)

    def download_song(self, song_url, filepath):
        resp = self.parse_url(song_url)
        decoded_resp = resp.decode()
        html_ele = etree.HTML(resp.decode())
        song_name = html_ele.xpath('//em[@class="f-ff2"]/text()')[0]
        song_id = song_url.split('=')[-1]
        song_content, music_format = self.get_song_content(song_id)
        self.save_song(song_name, music_format, song_content, filepath)

    def main(self):
        resp = self.parse_url('http://music.163.com/#/song?id=33854162')
        decoded = resp.decode()
        html_ele = etree.HTML(decoded)
        song_name = html_ele.xpath('//em[@class="f-ff2"]/text()')[0]

if __name__ == '__main__':
    netease = MusicDownloader()
    netease.main()
