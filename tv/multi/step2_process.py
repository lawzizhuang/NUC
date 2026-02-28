import re, os

class IPTVMirger:
    def __init__(self):
        self.alias_map = {}; self.std_info = {}

    def clean_name(self, name):
        n = name.upper()
        for s in ["SD","HD","4K","蓝光","超清","标清","频道","(",")","（","）","-","_"]:
            n = n.replace(s, "")
        return re.sub(r'[^\w\u4e00-\u9fa5]', '', n).strip()

    def load_template(self):
        if not os.path.exists("template_new.txt"): return False
        current_group = "其他频道"
        with open("template_new.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if "#genre#" in line:
                    current_group = line.split(',')[0].strip(); continue
                try:
                    meta, aliases = line.replace('：', ':').split(':', 1)
                    parts = meta.split(',')
                    tid, std_name = parts[0], parts[1]
                    logo = parts[2] if len(parts) > 2 else ""
                    self.std_info[std_name] = {"id": tid, "logo": logo, "group": current_group}
                    for a in aliases.split('#') + [std_name]:
                        self.alias_map[self.clean_name(a)] = std_name
                except: continue
        return True

    def run(self):
        if not self.load_template(): return
        input_files = [f for f in os.listdir('.') if f.endswith('.m3u') and f not in ["merged_raw.m3u", "final_cleaned.m3u", "final_standard.m3u"]]
        with open("merged_raw.m3u", 'w', encoding='utf-8') as out_f:
            out_f.write("#EXTM3U\n")
            for file in input_files:
                with open(file, 'r', encoding='utf-8', errors='ignore') as in_f:
                    content = in_f.read()
                    matches = re.findall(r'(?:#EXTINF:.*?,|^(?!http))(.+?)\n(http.*?)$', content, re.M)
                    for name, url in matches:
                        std_name = self.alias_map.get(self.clean_name(name))
                        if std_name:
                            info = self.std_info[std_name]
                            out_f.write(f'#EXTINF:-1 tvg-id="{info["id"]}" tvg-name="{std_name}" tvg-logo="{info["logo"]}" group-title="{info["group"]}",{std_name}\n{url.strip()}\n')
        print("✅ 已生成 merged_raw.m3u")

if __name__ == "__main__":
    IPTVMirger().run()