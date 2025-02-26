from pathlib import Path
import requests
from collections import defaultdict

def convert_surge_to_clash(surge_rule):
    # 如果是以点开头的纯域名
    if surge_rule.startswith('.'):
        domain = surge_rule[1:]  # 移除开头的点
        return f"- DOMAIN-SUFFIX,{domain},REJECT"
    
    # 如果不是以点开头，但也没有逗号（可能是完整域名）
    if not surge_rule.startswith('#') and ',' not in surge_rule and surge_rule.strip():
        return f"- DOMAIN,{surge_rule.strip()},REJECT"

    # 原有的 Surge 规则转换逻辑
    if not surge_rule or surge_rule.startswith('#'):
        return None
        
    parts = surge_rule.strip().split(',')
    if len(parts) < 2:
        return None
        
    rule_type = parts[0]
    
    if rule_type in ['DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 
                     'GEOIP', 'PROCESS-NAME']:
        return f"- {','.join(parts)}"
        
    elif rule_type in ['IP-CIDR', 'IP-CIDR6']:
        if len(parts) == 3:
            return f"- {','.join(parts)},no-resolve"
        return f"- {surge_rule},no-resolve"
        
    elif rule_type == 'URL-REGEX':
        keyword = parts[1].replace('^', '').replace('$', '')
        return f"- DOMAIN-KEYWORD,{keyword},{parts[2]}"
        
    elif rule_type == 'USER-AGENT':
        return f"# {surge_rule} (USER-AGENT not supported in Clash)"
        
    return None

def main():
    rules_file = Path('rules.txt')
    if not rules_file.exists():
        print("rules.txt not found")
        return

    rules_dir = Path('rules')
    rules_dir.mkdir(exist_ok=True)

    # 删除 rules 目录下的所有 yaml 文件
    for file in rules_dir.glob('*.yaml'):
        file.unlink()

    # 用于存储同名文件的规则
    rules_dict = defaultdict(set)
    
    with open(rules_file, 'r') as f:
        urls = f.read().splitlines()

    for url in urls:
        if not url or url.startswith('#'):
            continue

        try:
            response = requests.get(url)
            surge_rules = response.text.splitlines()

            # 获取基础文件名（移除 .list 扩展名）
            base_name = Path(url).stem.replace('.list', '')
            
            # 转换规则并添加到对应的文件名集合中
            for rule in surge_rules:
                if rule and not rule.startswith('#'):
                    converted_rule = convert_surge_to_clash(rule.strip())
                    if converted_rule:
                        rules_dict[base_name].add(converted_rule)

            print(f"Processed {url}")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")

    # 写入合并后的文件
    for base_name, rules in rules_dict.items():
        output_file = rules_dir / f"{base_name}.yaml"
        
        # 将规则按字母顺序排序并去重
        sorted_rules = sorted(list(rules))
        
        # 写入文件
        with open(output_file, 'w') as f:
            f.write("payload:\n")
            f.write('\n'.join(sorted_rules))
            
        print(f"Created {output_file} with {len(sorted_rules)} rules")

if __name__ == '__main__':
    main()
