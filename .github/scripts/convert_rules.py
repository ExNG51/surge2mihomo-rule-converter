import re
import requests
from pathlib import Path

def convert_surge_to_clash(surge_rule):
    # 根据需要添加转换逻辑
    # 这里是一个简单的示例
    if surge_rule.startswith('DOMAIN-SUFFIX'):
        return surge_rule.replace('DOMAIN-SUFFIX', 'DOMAIN-SUFFIX')
    elif surge_rule.startswith('DOMAIN'):
        return surge_rule.replace('DOMAIN', 'DOMAIN')
    elif surge_rule.startswith('IP-CIDR'):
        return surge_rule
    return None

def main():
    # 读取 rules.txt
    rules_file = Path('rules.txt')
    if not rules_file.exists():
        print("rules.txt not found")
        return

    # 确保 rules 目录存在
    rules_dir = Path('rules')
    rules_dir.mkdir(exist_ok=True)

    with open(rules_file, 'r') as f:
        urls = f.read().splitlines()

    for url in urls:
        if not url or url.startswith('#'):
            continue

        try:
            # 下载规则内容
            response = requests.get(url)
            surge_rules = response.text.splitlines()

            # 转换规则
            clash_rules = []
            for rule in surge_rules:
                if rule and not rule.startswith('#'):
                    converted_rule = convert_surge_to_clash(rule)
                    if converted_rule:
                        clash_rules.append(converted_rule)

            # 生成输出文件名
            output_file = rules_dir / f"{Path(url).stem.replace('.list', '')}.yaml"
            
            # 写入转换后的规则
            with open(output_file, 'w') as f:
                f.write('\n'.join(clash_rules))
                
            print(f"Converted {url} to {output_file}")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")

if __name__ == '__main__':
    main()
