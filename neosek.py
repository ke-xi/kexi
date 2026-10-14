# coding=utf-8
# NeoSekai 综合站爬虫 - 适配动画/漫画/音声/小说四类内容
import base64
from html import unescape
import json
import re
import sys
import urllib.parse
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    host = 'https://neosek.ai'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://neosek.ai/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'application/json, text/plain, */*',
    }

    # 按截图分类
    cates = [
        ('动画', 'anime'),
        ('漫画', 'manga'),
        ('音声', 'asmr'),
        ('小说', 'novel'),
    ]

    # 列表页筛选参数映射（按截图）
    FILTERS = {
        'anime': [
            {'key': 'type', 'name': '类型', 'value': [
                {'n': '全部', 'v': ''}, {'n': 'TV', 'v': 'TV'},
                {'n': '剧场版', 'v': '剧场版'}, {'n': 'OVA/OAD', 'v': 'OVA'},
                {'n': 'WEB', 'v': 'WEB'},
            ]},
            {'key': 'genre', 'name': '题材', 'value': [
                {'n': '全部', 'v': ''}, {'n': '日本', 'v': '日本'},
                {'n': '恋爱', 'v': '恋爱'}, {'n': '搞笑', 'v': '搞笑'},
                {'n': '漫画改', 'v': '漫画改'},
            ]},
            {'key': 'year', 'name': '年份', 'value': [
                {'n': '全部', 'v': ''}, {'n': '2026', 'v': '2026'},
                {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'},
                {'n': '2023', 'v': '2023'},
            ]},
            {'key': 'rating', 'name': '分级', 'value': [
                {'n': '全部', 'v': ''}, {'n': '全年龄', 'v': '全年龄'},
                {'n': 'R15', 'v': 'R15'}, {'n': 'R18', 'v': 'R18'},
            ]},
            {'key': 'sort', 'name': '排序', 'value': [
                {'n': '最新', 'v': 'latest'}, {'n': '最近更新', 'v': 'updated'},
                {'n': '热度', 'v': 'popular'}, {'n': '发行日期', 'v': 'release'},
                {'n': '人气', 'v': 'views'},
            ]},
        ],
        'manga': [
            {'key': 'genre', 'name': '题材', 'value': [
                {'n': '全部', 'v': ''}, {'n': '日本', 'v': '日本'},
                {'n': '恋爱', 'v': '恋爱'}, {'n': '搞笑', 'v': '搞笑'},
            ]},
            {'key': 'sort', 'name': '排序', 'value': [
                {'n': '最新', 'v': 'latest'}, {'n': '最近更新', 'v': 'updated'},
                {'n': '热度', 'v': 'popular'},
            ]},
        ],
        'asmr': [
            {'key': 'type', 'name': '类型', 'value': [
                {'n': '全部', 'v': ''}, {'n': '同人音声(ASMR)', 'v': 'ASMR'},
                {'n': '广播剧/Drama CD', 'v': 'Drama CD'},
            ]},
            {'key': 'genre', 'name': '题材', 'value': [
                {'n': '全部', 'v': ''}, {'n': '内射/中出', 'v': '内射'},
                {'n': 'ASMR', 'v': 'ASMR'}, {'n': '亲热/甜蜜', 'v': '亲热'},
            ]},
            {'key': 'sort', 'name': '排序', 'value': [
                {'n': '最新', 'v': 'latest'}, {'n': '最近更新', 'v': 'updated'},
                {'n': '热度', 'v': 'popular'}, {'n': '发行日期', 'v': 'release'},
            ]},
        ],
        'novel': [
            {'key': 'type', 'name': '类型', 'value': [
                {'n': '全部', 'v': ''}, {'n': '轻小说', 'v': '轻小说'},
                {'n': '网络小说', 'v': '网络小说'}, {'n': '同人小说', 'v': '同人小说'},
            ]},
            {'key': 'genre', 'name': '题材', 'value': [
                {'n': '全部', 'v': ''}, {'n': '日本', 'v': '日本'},
                {'n': '后宫', 'v': '后宫'}, {'n': '恋爱', 'v': '恋爱'},
                {'n': '校园', 'v': '校园'}, {'n': '奇幻', 'v': '奇幻'},
            ]},
            {'key': 'sort', 'name': '排序', 'value': [
                {'n': '最新', 'v': 'latest'}, {'n': '最近更新', 'v': 'updated'},
                {'n': '热度', 'v': 'popular'}, {'n': '字数', 'v': 'words'},
            ]},
        ],
    }

    def getName(self):
        return 'NeoSekai'

    def init(self, extend=''):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    # ---------- 封面代理 ----------

    @staticmethod
    def _cover_host(url):
        try:
            parts = urllib.parse.urlsplit(url)
            return (parts.scheme == 'https' and parts.port in (None, 443)
                    and not parts.username and not parts.password
                    and parts.hostname in ('neosek.ai', 'www.neosek.ai',
                                           'cdn.neosek.ai', 'img.neosek.ai'))
        except (ValueError, TypeError):
            return False

    def _cover_pic(self, url, vid):
        url = unescape(url or '').strip()
        if not self._cover_host(url):
            return url
        try:
            parts = urllib.parse.urlsplit(self.getProxyUrl())
            query = dict(urllib.parse.parse_qsl(parts.query))
            key = str(getattr(self, 'siteKey', '') or query.get('siteKey', ''))
            if key and parts.scheme in ('http', 'https') and parts.netloc:
                token = base64.urlsafe_b64encode(url.encode()).decode().rstrip('=')
                query.update(type='cover', image=token, vid=str(vid),
                             siteKey=key, cover_rev='2')
                return urllib.parse.urlunsplit((parts.scheme, parts.netloc,
                                                parts.path,
                                                urllib.parse.urlencode(query), ''))
        except Exception:
            pass
        return url

    def localProxy(self, param):
        if not isinstance(param, dict) or param.get('type') != 'cover':
            return [400, 'text/plain', b'Invalid cover request', {}]
        try:
            token = param.get('image', '')
            vid = str(param.get('vid', ''))
            if (not isinstance(token, str) or len(token) > 16384
                    or not re.fullmatch(r'[A-Za-z0-9_-]+', token)
                    or not re.fullmatch(r'\d+', vid)):
                return [400, 'text/plain', b'Invalid cover request', {}]
            url = base64.urlsafe_b64decode(
                token + '=' * (-len(token) % 4)).decode()
        except (ValueError, UnicodeError):
            return [400, 'text/plain', b'Invalid cover URL', {}]
        import requests
        headers = dict(self.headers)
        headers['Referer'] = self.host + '/'
        try:
            for _ in range(4):
                if not self._cover_host(url):
                    return [403, 'text/plain', b'Cover host not allowed', {}]
                with requests.get(url, headers=headers, timeout=(5, 10),
                                  allow_redirects=False, stream=True) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        if not response.headers.get('Location'):
                            break
                        url = urllib.parse.urljoin(
                            url, response.headers['Location'])
                        continue
                    if response.status_code != 200:
                        break
                    chunks, size = [], 0
                    for chunk in response.iter_content(65536):
                        size += len(chunk)
                        if size > 5 * 1024 * 1024:
                            raise ValueError('Image too large')
                        chunks.append(chunk)
                    data = self._sanitize_jpeg(b''.join(chunks))
                    mime = self._image_mime(data)
                    if mime:
                        return [200, mime, data,
                                {'Cache-Control': 'private, max-age=300'}]
                    break
        except (requests.RequestException, ValueError):
            pass
        return [502, 'text/plain', b'Cover unavailable',
                {'Cache-Control': 'no-store'}]

    @staticmethod
    def _image_mime(data):
        if data.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        if data.startswith((b'GIF87a', b'GIF89a')):
            return 'image/gif'
        if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return 'image/webp'
        return ''

    @staticmethod
    def _valid_exif_header(payload):
        tiff = payload[6:]
        if len(tiff) < 8 or tiff[:4] not in (b'II\x2a\x00', b'MM\x00\x2a'):
            return False
        order = 'little' if tiff[:2] == b'II' else 'big'
        offset = int.from_bytes(tiff[4:8], order)
        if offset < 8 or offset + 2 > len(tiff):
            return False
        count = int.from_bytes(tiff[offset:offset + 2], order)
        if offset + 2 + count * 12 + 4 > len(tiff):
            return False
        for index in range(count):
            entry = tiff[offset + 2 + index * 12:offset + 14 + index * 12]
            tag = int.from_bytes(entry[:2], order)
            if tag == 0x0112:
                kind = int.from_bytes(entry[2:4], order)
                components = int.from_bytes(entry[4:8], order)
                orientation = int.from_bytes(entry[8:10], order)
                if kind != 3 or components != 1 or not 1 <= orientation <= 8:
                    return False
        return True

    @classmethod
    def _sanitize_jpeg(cls, data):
        if not data.startswith(b'\xff\xd8'):
            return data
        pieces = [data[:2]]
        pos = 2
        changed = False
        while pos < len(data):
            start = pos
            if data[pos] != 0xff:
                return data
            while pos < len(data) and data[pos] == 0xff:
                pos += 1
            if pos >= len(data):
                return data
            marker = data[pos]
            pos += 1
            if marker in (0xda, 0xd9):
                return b''.join(pieces) + data[start:] if changed else data
            if marker in (0xd8, 0x01) or 0xd0 <= marker <= 0xd7:
                pieces.append(data[start:pos])
                continue
            if marker == 0 or pos + 2 > len(data):
                return data
            length = int.from_bytes(data[pos:pos + 2], 'big')
            end = pos + length
            if length < 2 or end > len(data):
                return data
            payload = data[pos + 2:end]
            bad_exif = (marker == 0xe1 and payload.startswith(b'Exif\x00\x00')
                        and not cls._valid_exif_header(payload))
            if bad_exif:
                changed = True
            else:
                pieces.append(data[start:end])
            pos = end
        return data

    # ---------- 请求封装 ----------

    def _get_html(self, url):
        try:
            return self.fetch(url, headers=self.headers, timeout=15).text
        except Exception:
            import requests
            return requests.get(url, headers=self.headers, timeout=15).text

    def _api(self, path, params=None):
        url = '{}/api{}'.format(self.host, path)
        if params:
            url += '?' + urllib.parse.urlencode(params)
        try:
            resp = self.fetch(url, headers=self.headers, timeout=15)
            return resp.json() if resp else {}
        except Exception:
            try:
                import requests
                r = requests.get(url, headers=self.headers, timeout=15)
                return r.json() if r.status_code == 200 else {}
            except Exception:
                return {}

    def _meta(self, html, prop):
        m = re.search(r'<meta[^>]+property="%s"[^>]+content="([^"]*)"' % prop,
                      html)
        if not m:
            m = re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="%s"'
                          % prop, html)
        return m.group(1).strip() if m else ''

    # ---------- 首页与分类 ----------

    def homeContent(self, filter):
        classes = [{'type_name': n, 'type_id': v} for n, v in self.cates]
        filters = {}
        for _, v in self.cates:
            filters[v] = self.FILTERS.get(v, [])
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        html = self._get_html(self.host)
        return {'list': self._parse_next_data(html, 'anime')[:30]}

    def categoryContent(self, tid, pg, filter, extend):
        params = {'page': pg, 'limit': 30}
        if extend:
            for k in ('type', 'genre', 'year', 'rating', 'sort'):
                if extend.get(k):
                    params[k] = extend[k]
        path = '/{}'.format(tid)
        data = self._api(path, params)
        videos = self._parse_api_list(data, tid)
        if not videos:
            url = '{}/{}?page={}'.format(self.host, tid, pg)
            if extend:
                for k, v in extend.items():
                    if v:
                        url += '&{}={}'.format(k, urllib.parse.quote(v))
            html = self._get_html(url)
            videos = self._parse_next_data(html, tid)
        return {
            'list': videos,
            'page': int(pg),
            'pagecount': int(pg) + (1 if len(videos) >= 20 else 0),
            'limit': 30,
            'total': 999999
        }

    def searchContent(self, key, quick, pg='1'):
        params = {'q': key, 'page': pg, 'limit': 30}
        data = self._api('/search', params)
        videos = self._parse_api_list(data, 'search')
        if not videos:
            url = '{}/search?q={}&page={}'.format(
                self.host, urllib.parse.quote(key), pg)
            html = self._get_html(url)
            videos = self._parse_next_data(html, 'search')
        return {'list': videos, 'page': int(pg)}

    # ---------- 详情 ----------

    def detailContent(self, ids):
        raw = ids[0]
        if ':' in raw:
            ctype, cid = raw.split(':', 1)
        else:
            ctype, cid = 'anime', raw

        # 尝试 API
        data = self._api('/works/{}'.format(cid))
        if data:
            return self._detail_from_api(data, ctype, cid)

        # 回退到 HTML 解析
        html = self._get_html('{}/{}/{}'.format(self.host, ctype, cid))
        return self._detail_from_html(html, ctype, cid)

    def _detail_from_api(self, data, ctype, cid):
        title = data.get('title') or data.get('name', '')
        pic = data.get('cover') or data.get('poster', '')
        desc = data.get('description') or data.get('summary', '')
        episodes = []

        for ep in (data.get('episodes') or data.get('chapters') or
                   data.get('tracks') or []):
            episodes.append({
                'name': ep.get('title') or ep.get('name', ''),
                'vid': str(ep.get('id', ''))
            })

        if not episodes:
            episodes = [{'name': title or cid, 'vid': cid}]

        play_url = '#'.join(
            '{}${}'.format(ep['name'].replace('#', '＃'), ep['vid'])
            for ep in episodes
        )
        vod = {
            'vod_id': '{}:{}'.format(ctype, cid),
            'vod_name': title,
            'vod_pic': self._cover_pic(pic, cid),
            'vod_content': desc,
            'vod_play_from': 'NeoSekai',
            'vod_play_url': play_url,
        }
        return {'list': [vod]}

    def _detail_from_html(self, html, ctype, cid):
        title = self._meta(html, 'og:title')
        pic = self._meta(html, 'og:image')
        desc = self._meta(html, 'og:description')
        episodes = self._extract_next_playlist(html, cid, title)
        play_url = '#'.join(
            '{}${}'.format(ep['name'].replace('#', '＃'), ep['vid'])
            for ep in episodes
        )
        vod = {
            'vod_id': '{}:{}'.format(ctype, cid),
            'vod_name': title,
            'vod_pic': self._cover_pic(pic, cid),
            'vod_content': desc,
            'vod_play_from': 'NeoSekai',
            'vod_play_url': play_url,
        }
        return {'list': [vod]}

    # ---------- 播放 ----------

    def playerContent(self, flag, id, vipFlags):
        raw = id.split('#')[0].strip()
        if ':' in raw:
            ctype, cid = raw.split(':', 1)
        else:
            ctype, cid = 'anime', raw

        if ctype == 'novel':
            return {
                'parse': 1,
                'url': '{}/novel/read/{}'.format(self.host, cid),
                'header': self.headers
            }
        if ctype == 'manga':
            return {
                'parse': 1,
                'url': '{}/manga/read/{}'.format(self.host, cid),
                'header': self.headers
            }

        # 视频/音声：尝试从 API 获取流地址
        data = self._api('/works/{}/play'.format(cid))
        if data and data.get('url'):
            return {
                'parse': 0,
                'url': data['url'],
                'header': self.headers
            }

        # 回退到 HTML 提取
        html = self._get_html('{}/{}/{}'.format(self.host, ctype, cid))
        play = ''
        m = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', html)
        if m:
            play = m.group(1).replace('\\/', '/')
        if not play:
            m = re.search(r'(https?://[^\s\'"]+\.(?:m3u8|mp4)[^\s\'"]*)', html)
            if m:
                play = m.group(1)
        return {
            'parse': 0 if play else 1,
            'url': play or '{}/{}/{}'.format(self.host, ctype, cid),
            'header': self.headers
        }

    # ---------- Next.js 数据解析 ----------

    def _parse_next_data(self, html, ctype):
        """从 Next.js 注入的 self.__next_f.push 数据中提取卡片列表"""
        videos = []
        seen = set()
        # 提取 __next_f.push 中的数据块
        chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
        for chunk in chunks:
            # 反转义
            chunk = chunk.replace('\\"', '"').replace('\\n', '\n')
            # 查找条目模式
            for m in re.finditer(
                r'\{[^{}]*"id"\s*:\s*(\d+)[^{}]*"title"\s*:\s*"([^"]*)"'
                r'[^{}]*"cover"\s*:\s*"([^"]*)"', chunk
            ):
                vid = m.group(1)
                if vid in seen:
                    continue
                seen.add(vid)
                videos.append({
                    'vod_id': '{}:{}'.format(ctype, vid),
                    'vod_name': m.group(2),
                    'vod_pic': self._cover_pic(m.group(3), vid),
                    'vod_remarks': ''
                })
        # 回退：从 HTML 卡片链接提取
        if not videos:
            videos = self._parse_html_cards(html, ctype)
        return videos

    def _parse_api_list(self, data, ctype):
        """从 API JSON 响应中提取列表"""
        videos = []
        seen = set()
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ('data', 'list', 'items', 'results', 'works'):
                if isinstance(data.get(key), list):
                    items = data[key]
                    break
        for item in items:
            vid = str(item.get('id', ''))
            if not vid or vid in seen:
                continue
            seen.add(vid)
            title = item.get('title') or item.get('name', '')
            pic = item.get('cover') or item.get('poster', '')
            if not title:
                continue
            videos.append({
                'vod_id': '{}:{}'.format(ctype, vid),
                'vod_name': title,
                'vod_pic': self._cover_pic(pic, vid),
                'vod_remarks': ''
            })
        return videos

    def _parse_html_cards(self, html, ctype):
        """从 HTML 中提取卡片链接"""
        videos = []
        seen = set()
        pattern = re.compile(
            r'<a[^>]+href="/(?:' + ctype + r')/(\d+)"[^>]*>(.*?)</a>',
            re.S
        )
        for m in pattern.finditer(html):
            vid = m.group(1)
            if vid in seen:
                continue
            inner = m.group(2)
            title = ''
            t = re.search(r'class="[^"]*(?:title|name)[^"]*"[^>]*>\s*([^<]+?)\s*<', inner, re.S)
            if t:
                title = t.group(1).strip()
            if not title:
                t = re.search(r'<img[^>]+alt="([^"]+)"', inner)
                if t:
                    title = t.group(1).strip()
            if not title:
                continue
            pic = ''
            for img in re.findall(r'<img[^>]+(?:data-src|src)="(http[^"]+)"', inner):
                if any(x in img for x in ('.gif', 'icon', 'avatar', 'logo')):
                    continue
                pic = img
                break
            seen.add(vid)
            videos.append({
                'vod_id': '{}:{}'.format(ctype, vid),
                'vod_name': title,
                'vod_pic': self._cover_pic(pic, vid),
                'vod_remarks': ''
            })
        return videos

    def _extract_next_playlist(self, html, current_vid, current_title):
        """从 Next.js 数据中提取剧集/章节列表"""
        episodes = []
        seen = set()
        chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
        for chunk in chunks:
            chunk = chunk.replace('\\"', '"').replace('\\n', '\n')
            # 匹配剧集/章节条目
            for m in re.finditer(
                r'\{[^{}]*"id"\s*:\s*(\d+)[^{}]*"title"\s*:\s*"([^"]*)"', chunk
            ):
                ep_vid = m.group(1)
                ep_name = m.group(2).strip()
                if ep_vid not in seen and ep_name:
                    seen.add(ep_vid)
                    episodes.append({'name': ep_name, 'vid': ep_vid})

        # 回退：HTML 中的剧集链接
        if not episodes:
            for m in re.finditer(
                r'<a[^>]+href="[^"]*?/(?:ep|ch|track)/(\d+)"[^>]*>\s*([^<]{1,80}?)\s*</a>',
                html, re.S
            ):
                ep_vid = m.group(1)
                ep_name = m.group(2).strip()
                if ep_name and ep_vid not in seen:
                    seen.add(ep_vid)
                    episodes.append({'name': ep_name, 'vid': ep_vid})

        if not episodes:
            return [{'name': current_title or current_vid, 'vid': current_vid}]

        if not any(e['vid'] == current_vid for e in episodes):
            episodes.insert(0, {'name': current_title or current_vid,
                                'vid': current_vid})

        def _ep_num(ep):
            m = re.search(r'(\d+)\s*$', ep['name'])
            return int(m.group(1)) if m else 0
        try:
            episodes.sort(key=_ep_num)
        except Exception:
            pass

        cur_idx = next(
            (i for i, e in enumerate(episodes) if e['vid'] == current_vid), None
        )
        if cur_idx is not None and cur_idx != 0:
            cur_ep = episodes.pop(cur_idx)
            episodes.insert(0, cur_ep)
        return episodes