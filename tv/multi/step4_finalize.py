import gzip, xml.etree.ElementTree as ET, re, os

# 配置
BACK_LIST = ["CGTN", "4K", "欧洲", "美洲", "测试", "俄语", "法语", "西语", "阿语"]
FORCED_IDS = {"CCTV16 4K": "CCTV16", "CCTV4K": "106"}

def finalize():
    epg_data = {}
    try:
        with gzip.open('e1.xml.gz', 'rb') as f:
            for _, elem in ET.iterparse(f, events=('end',)):
                if elem.tag == 'channel':
                    c_id = elem.get('id')
                    logo = elem.find('icon').get('src') if elem.find('icon') is not None else ""
                    names = [n.text.strip().upper() for n in elem.findall('display-name') if n.text]
                    for n in names:
                        epg_data[n] = {"id": c_id, "logo": logo}
                        epg_data[n.replace('-', '')] = {"id": c_id, "logo": logo}
                    elem.clear()
    except: pass

    channels = []; seen_urls = set(); group_order = []
    with open("final_cleaned.m3u", 'r', encoding='utf-8') as f:
        matches = re.findall(r'(#EXTINF:.*?,(.*?))\n(http.*?)$', f.read(), re.M)
        for full_info, name, url in matches:
            url = url.strip()
            if url in seen_urls: continue
            seen_urls.add(url)
            
            name_c = name.strip()
            group = re.search(r'group-title="(.*?)"', full_info).group(1)
            if group not in group_order: group_order.append(group)
            
            match = epg_data.get(FORCED_IDS.get(name_c, name_c).upper())
            f_id = match['id'] if match else "0"
            f_logo = match['logo'] if match else ""
            
            try: sid = int(f_id)
            except: sid = 9999
            weight = sid + 10000 if any(kw in name_c for kw in BACK_LIST) else sid

            info = f'#EXTINF:-1 tvg-id="{f_id}" tvg-name="{name_c}" tvg-logo="{f_logo}" group-title="{group}",{name_c}'
            channels.append({"group": group, "weight": weight, "name": name_c, "content": f"{info}\n{url}"})

    channels.sort(key=lambda x: (group_order.index(x['group']), x['weight'], x['name']))
    with open("final_standard.m3u", 'w', encoding='utf-8') as f:
        f.write('#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e1.xml.gz"\n')
        for ch in channels: f.write(f"{ch['content']}\n")
    print("✨ 终极播放列表 final_standard.m3u 已生成！")

if __name__ == "__main__":
    finalize()