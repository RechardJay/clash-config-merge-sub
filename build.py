import requests
import yaml

# 下载 1~6 号配置
URLS = [
    f"https://gitlab.com/free9999/ipupdate/-/raw/master/backup/img/1/2/ipp/clash.meta2/{i}/config.yaml"
    for i in range(1, 7)
]

OUTPUT = "alvin_merged.yaml"

def main():
    all_proxies = []
    print("正在下载 1~6 配置文件...")
    i = 1
    for url in URLS:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            print(f"成功下载配置文件{i}")
            i+=1
            cfg = yaml.safe_load(r.text)
            if "proxies" in cfg:
                all_proxies.extend(cfg["proxies"])
                print(f"获取代理{cfg["proxies"][0]}")
        except Exception as e:
            print(f"下载失败: {url[:50]} | {e}")

    # 去重：server + port + type（支持 IPv4 + IPv6）
    unique = {}
    for p in all_proxies:
        s = p.get("server", "")
        pt = p.get("port", "")
        t = p.get("type", "")
        key = (s, pt, t)
        if key not in unique:
            unique[key] = p
            print(f"添加代理：{s}:{t}")
        else:
            print(f"跳过{s}:{p}")
    plist = list(unique.values())

    # 重命名为 节点01、02、03...
    for i, p in enumerate(plist):
        p["name"] = f"节点{i+1:02d}"

    proxy_names = [p["name"] for p in plist]

    # ===================== 最终固定配置 =====================
    final = {
        "mixed-port": 7890,
        "allow-lan": False,
        "log-level": "info",
        "mode": "rule",
        "secret": "github.com/Alvin9999-newpac_fanqiang",

        "dns": {
            "enabled": True,
            "nameserver": ["119.29.29.29", "223.5.5.5"],
            "fallback-filter": {
                "geoip": False,
                "ipcidr": ["240.0.0.0/4", "0.0.0.0/32"]
            }
        },

        "proxies": plist,

        "proxy-groups": [
            {
                "name": "🚀 代理选择",
                "type": "select",
                "proxies": ["⚡ 自动选择"] + proxy_names + ["DIRECT"]
            },
            {
                "name": "⚡ 自动选择",
                "type": "fallback",
                "url": "https://www.gstatic.com/generate_204",
                "interval": 5,
                "proxies": proxy_names
            },
            {
                "name": "🛑 广告拦截",
                "type": "select",
                "proxies": ["REJECT", "DIRECT"]
            }
        ],

        "rules": [
            "GEOIP,LAN,DIRECT,no-resolve",
            "GEOSITE,CN,DIRECT",
            "GEOIP,CN,DIRECT",
            "MATCH,🚀 代理选择"
        ]
    }

    # 保存
    with open(OUTPUT, "w", encoding="utf-8") as f:
        yaml.dump(final, f, allow_unicode=True, sort_keys=False, indent=2)

    print(f"\n✅ 生成完成：{OUTPUT}")
    print(f"📶 节点总数：{len(plist)}")

if __name__ == "__main__":
    main()