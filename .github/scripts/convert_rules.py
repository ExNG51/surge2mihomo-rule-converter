def convert_surge_to_clash(surge_rule):
    if not surge_rule or surge_rule.startswith('#'):
        return None
        
    parts = surge_rule.strip().split(',')
    if len(parts) < 2:
        return None
        
    rule_type = parts[0]
    
    # 基础规则转换
    if rule_type in ['DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 
                     'GEOIP', 'PROCESS-NAME']:
        # 确保添加 "- " 前缀，并正确组合规则
        return f"- {','.join(parts)}"
        
    # IP-CIDR 规则特殊处理
    elif rule_type in ['IP-CIDR', 'IP-CIDR6']:
        # 添加 no-resolve 选项
        if len(parts) == 3:
            return f"- {','.join(parts)},no-resolve"
        return f"- {surge_rule},no-resolve"
        
    # URL-REGEX 在 Clash 中不支持，可以转换为 DOMAIN-KEYWORD
    elif rule_type == 'URL-REGEX':
        keyword = parts[1].replace('^', '').replace('$', '')
        return f"- DOMAIN-KEYWORD,{keyword},{parts[2]}"
        
    # USER-AGENT 规则在 Clash 中不支持，可以忽略或转换为注释
    elif rule_type == 'USER-AGENT':
        return f"# {surge_rule} (USER-AGENT not supported in Clash)"
        
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
            clash_rules.append("payload:")  # 添加 YAML 头部
            
            for rule in surge_rules:
                if rule and not rule.startswith('#'):
                    converted_rule = convert_surge_to_clash(rule)
                    if converted_rule:
                        clash_rules.append(converted_rule)

            # 保持原名，仅将扩展名改为 .yaml
            output_file = rules_dir / f"{Path(url).stem.replace('.list', '')}.yaml"
            
            # 写入转换后的规则
            with open(output_file, 'w') as f:
                f.write('\n'.join(clash_rules))
                
            print(f"Converted {url} to {output_file}")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")

if __name__ == '__main__':
    main()
