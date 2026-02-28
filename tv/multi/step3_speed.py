import json, re, threading, subprocess, requests, os
from queue import Queue

INPUT_FILE = "merged_raw.m3u"
OUTPUT_FILE = "final_cleaned.m3u"

class IPTVChecker:
    def __init__(self):
        self.results = []; self.lock = threading.Lock()

    def get_height(self, url):
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=height', '-of', 'json', '-timeout', '5000000', url]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=7)
            return int(json.loads(res.stdout)['streams'][0].get('height', 0))
        except: return 0

    def worker(self, q):
        while True:
            item = q.get()
            if item is None: break
            name, url, meta = item
            try:
                r = requests.get(url, timeout=3, stream=True)
                if r.status_code == 200:
                    h = self.get_height(url)
                    if h >= 720: # 仅保留高清
                        with self.lock:
                            self.results.append({"meta": meta, "url": url, "name": name, "latency": r.elapsed.total_seconds()})
            except: pass
            q.task_done()

    def run(self):
        if not os.path.exists(INPUT_FILE): return
        tasks = []
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            matches = re.findall(r'(#EXTINF:.*?,(.*?))\n(http.*?)$', f.read(), re.M)
            for m in matches: tasks.append((m[1].strip(), m[2].strip(), m[0].strip()))
        
        q = Queue()
        for t in tasks: q.put(t)
        for _ in range(15): threading.Thread(target=self.worker, args=(q,), daemon=True).start()
        q.join()

        self.results.sort(key=lambda x: (x['name'], x['latency']))
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for r in self.results: f.write(f"{r['meta']}\n{r['url']}\n")
        print(f"✅ 已生成 {OUTPUT_FILE}")

if __name__ == "__main__":
    IPTVChecker().run()