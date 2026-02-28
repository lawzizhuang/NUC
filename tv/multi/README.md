📺 IPTV 频道清洗与标准化操作手册
本套工具集旨在从杂乱的 .m3u 源文件中，自动化提取、测速、过滤高清频道，并最终对齐官方 EPG 节目单。

## 🛠️ 环境准备
运行环境：Python 3.10+

核心依赖：requests (网络请求), ffprobe (画质检测)。

安装命令：pip install requests

系统工具：确保系统已安装 ffmpeg（脚本需调用其中的 ffprobe）。

核心文件：

e1.xml.gz：官方 EPG 数据库文件（需定期更新以保持 ID 准确）。

template.txt：您的手工频道分类模板。

##  📂 自动化流水线 (4个步骤)
Step 1: 建立映射模板 (step1_meta.py)
触发条件：仅在 template.txt 发生大改动，或 EPG ID 大规模变化时运行。

功能：读取 EPG 数据库，为您的频道匹配唯一的 tvg-id 和台标 Logo。

输出：template_new.txt (这是后续合并步骤的灵魂文件)。

Step 2: 全量合并与分组 (step2_process.py)
触发条件：每次下载了新的 .m3u 源文件后运行。

功能：扫描当前文件夹下所有的 .m3u 文件，通过模糊匹配（别名系统）识别频道。

输出：merged_raw.m3u (包含所有识别到的源，格式已初步统一)。

Step 3: 测速与画质筛选 (step3_speed.py)
触发条件：合并完成后运行。

核心逻辑：

连通性测试：剔除无法连接的死链。

画质探测：调用 ffprobe 获取分辨率，自动删除高度 < 720 的标清源。

性能排序：相同频道按响应时间（Latency）从小到大排列。

输出：final_cleaned.m3u (只剩下高清、可用的精选源)。

Step 4: 最终标准化整理 (step4_finalize.py)
触发条件：测速筛选完成后运行。

功能：

注入头信息：加入 x-tvg-url 节目单声明。

台标补全：将官方 Logo 链接注入每个频道。

沉底排序：将 CGTN、4K、国际台等特定频道强制排在各自组别的末尾。

去重：物理地址（URL）完全一致的源仅保留一个。

输出：final_standard.m3u (这就是您最终使用的成品文件)。

##  🚀 日常更新三部曲 (常用操作)
当您收集到一批新的源（.m3u）放入文件夹后，只需按顺序执行：

python step2_process.py

python step3_speed.py

python step4_finalize.py

完成后，直接将 final_standard.m3u 导入您的播放器（如 TiviMate, PotPlayer）即可。

##  💡 维护小贴士
如何新增频道？：在 template.txt 中按 标准名：别名1#别名2 的格式添加，然后跑一遍 Step 1 即可。

为什么合并为空？：检查新源文件的名称是否与 template_new.txt 中的别名对得上。如果对不上，在模板里加个别名。

速度太慢？：Step 3 测速最耗时（因为要探测画质），可以适当调节脚本中的 THREADS 线程数（建议 10-20）。

排序微调：如果您想让某个词也沉底，只需编辑 step4_finalize.py 中的 BACK_LIST 列表。