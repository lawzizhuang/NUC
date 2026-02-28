import gzip
import xml.etree.ElementTree as ET
import os

def update_template_robust():
    epg_by_name = {}
    print("⏳ 正在读取 e1.xml.gz 以提取 ID 和 Logo...")
    try:
        with gzip.open('e1.xml.gz', 'rb') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag == 'channel':
                    c_id = elem.get('id', '0')
                    names = [n.text.strip() for n in elem.findall('display-name') if n.text]
                    logo = elem.find('icon').get('src', '') if elem.find('icon') is not None else ""
                    for n in names:
                        epg_by_name[n.upper()] = {"id": c_id, "logo": logo}
                    elem.clear()
    except Exception as e:
        print(f"❌ 失败: {e}"); return

    new_lines = []
    if os.path.exists('template.txt'):
        with open('template.txt', 'r', encoding='utf-8') as f:
            current_group = ""
            for line in f:
                line = line.strip()
                if not line: continue
                if "#genre#" in line:
                    new_lines.append(line)
                    continue
                try:
                    std_name, alias_str = line.replace('：', ':').split(':', 1)
                    # 匹配 ID 和 Logo
                    match = epg_by_name.get(std_name.strip().upper())
                    tid = match['id'] if match else "0"
                    logo = match['logo'] if match else ""
                    new_lines.append(f"{tid},{std_name.strip()},{logo}:{alias_str.strip()}")
                except: new_lines.append(line)

    with open('template_new.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("✨ template_new.txt 已生成。")

if __name__ == "__main__":
    update_template_robust()