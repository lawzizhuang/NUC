# N1 / Mihomo 兼容规则快照

配套模板：`../../ACL4SSR_n1.yaml`。

## 目的与参考

参考 [dler-io/Rules 的 Clash 提供者](https://github.com/dler-io/Rules/tree/main/Clash)：将带规则类型的条目放在 YAML `payload` 中，配置 `behavior: classical`、`format: yaml`。没有照搬其 DNS、端口、控制接口认证或 TUN 设置，也没有将整套 ACL4SSR 分类替换成 dler 分类。

当前 N1 内核拒绝 `URL-REGEX`。这些快照只移除该类型，保留其他非空、非注释规则及原始顺序，不将 URL 路径正则扩大成域名匹配。

| 文件 | 源文件 | 保留 | 移除 URL-REGEX |
| --- | --- | ---: | ---: |
| ChinaMedia.yaml | Clash/ChinaMedia.list | 37 | 1 |
| ProxyMedia.yaml | Clash/ProxyMedia.list | 371 | 1 |
| Download.yaml | Clash/Download.list | 15 | 7 |

源：[ACL4SSR/ACL4SSR](https://github.com/ACL4SSR/ACL4SSR)，固定提交 `3024bf8b2c9db5bf8807c4595674be8bbc22bd86`。
规则源许可为 [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)，派生规则文件按相同许可提供；修改为过滤不支持类型并转成 YAML。`build.py` 从指定 Git 提交读取原文，不读取工作区改动。

dler 参考时检查的提交为 `3ccf5720a78e34a71cf3b4f3abb8102e26e42aed`；未复制其规则内容。

## 更新

```sh
python3 clash/ruleset/n1/build.py /path/to/local/ACL4SSR
```

不自动联网、不安装依赖。源仓库 HEAD 必须等于脚本的 `REVISION`。升级时先审核上游差异，再修改固定提交、重新生成、检查 diff 并同步更新本表。遇到其他未知类型会在写文件前停止。

这些是静态快照，不自动跟随 ACL4SSR master 更新；模板里的其他 ACL4SSR HTTP 提供者仍跟随 master，并非全模板锁定版本。

`PROCESS-NAME` 原样保留，但 N1 一般无法识别被转发终端上的进程，不能依赖这些条目完成旁路由分流。

## 发布与应用边界

1. 将模板和本目录的三个 YAML 配套文件一起发布到目标 GitHub 分支；未发布前，模板新增的远程 URL 可能返回 404。发布后先验证三个文件均可下载且内容符合预期。
2. Sub-Store 若仍使用静态内嵌 YAML，仓库更新不会自动修改它。明确选择手动同步，或另行配置受控的远程读取流程。
3. 本地模板原有 41 条规则；设备此前检查到 42 条，包含额外的 `jianguoyun.com` 直连规则。应用前需比较 Sub-Store 当前定制；本次未擅自把设备差异写入模板。
4. 发布并不等于部署。生成产物、刷新 N1、重载均须单独安排与授权。
5. 应用后核对源/运行 YAML 的 behavior、format、provider 有效数量，以及新启动窗口内的格式/不支持类型告警。排查 DNS/端口/其他提供者错误，不能只看总规则数。
6. 用同一客户端、同一业务验证 CDN；没有新告警不能替代业务成功验证。本次改动不保证解决 CDN TCP 超时。

## 刻意保留的行为

- 不改 DNS 上游、fallback、Fake-IP 过滤或嗅探，不启用 HTTPDNS 屏蔽。
- 不改分流目标、AI 规则优先级、现有地域组及全球直连的可选出口。
- 仅为显式局域网 IP 规则添加 `no-resolve`，避免该 IP 规则为域名连接触发不必要解析。
- 修复所有 ACL4SSR `.list` 的 `format: text`，以及原本不存在的根目录细分规则 URL。

## 回滚

发布/部署前保留当前 Sub-Store 定义、N1 源配置和相应版本信息，备份中可能有凭据，应私密存储。回滚应恢复已确认可用的完整配置/产物，不要仅恢复存在缺失 format/错误路径的旧本地模板。若已部署兼容副本，不应先删除其远程文件，以免仍使用该模板的客户端更新失败。
