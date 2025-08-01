import requests
import json
import os
import time
import glob
import base64
from datetime import datetime, timedelta
from tqdm import tqdm
from typing import List, Dict, Optional, Tuple

"""
GitHub热门项目分析机器人
功能：
1. 获取GitHub近期热门项目数据
2. 使用AI分析项目技术亮点
3. 生成Markdown格式的洞察报告
4. 对比历史趋势变化
"""

def get_date_n_days_ago(days: int) -> str:
    """
    获取n天前的ISO格式日期字符串
    
    Args:
        days: 天数
        
    Returns:
        ISO格式日期字符串 (e.g., "2025-07-24T15:48:57Z")
    """
    dt = datetime.now() - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def build_trending_url(days: int = 7, limit: int = 10) -> str:
    """
    构建GitHub热门项目查询URL
    
    Args:
        days: 查询天数范围
        limit: 返回项目数量
        
    Returns:
        GitHub API查询URL
    """
    base_url = "https://api.github.com/search/repositories"
    since_date = get_date_n_days_ago(days)
    created_query = f"created:>{since_date}"
    return f"{base_url}?q={created_query}&sort=stars&order=desc&per_page={limit}"

def get_trending_repos(days: int = 7, limit: int = 10, token: Optional[str] = None) -> List[Dict]:
    """
    从GitHub API获取热门项目列表
    
    Args:
        days: 查询天数范围
        limit: 返回项目数量
        token: GitHub API令牌
        
    Returns:
        热门项目列表，每个项目为字典格式
    """
    url = build_trending_url(days, limit)
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        return response.json().get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取trending仓库失败: {e}")
        return []

from collections import Counter

def analyze_data(repos: List[Dict]) -> Optional[Dict]:
    """
    分析仓库数据，生成统计指标
    
    Args:
        repos: 仓库数据列表
        
    Returns:
        包含统计指标的字典:
        {
            "repo_count": 项目数量,
            "total_stars": 总星标数,
            "total_forks": 总Fork数,
            "language_stats": 语言分布统计
        }
    """
    if not repos:
        return None

    # 统计语言分布（处理None值）
    language_list = [repo['language'] or 'N/A' for repo in repos]
    language_stats = Counter(language_list)
    
    # 计算星标和Fork总数
    total_stars = sum(repo['stargazers_count'] for repo in repos)
    total_forks = sum(repo.get('forks_count', 0) for repo in repos)
    
    return {
        "repo_count": len(repos),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "language_stats": dict(language_stats.most_common())
    }

def print_console_report(repos: List[Dict], analysis_result: Dict):
    """
    在控制台打印分析报告
    
    Args:
        repos: 仓库数据列表
        analysis_result: 分析结果字典
    """
    # 报告头部
    header = "🔥 GitHub 热门项目洞察报告"
    separator = "=" * len(header)
    print(f"\n{separator}\n{header}\n{separator}")
    print(f"共找到 {analysis_result['repo_count']} 个热门项目")
    
    if not repos:
        print("⚠️ 没有找到热门项目")
        return
    
    # 打印每个项目详情
    for i, repo in enumerate(repos, 1):
        print(f"\n🏆 #{i} {repo['name']}")
        print(f"🔗 链接: {repo['html_url']}")
        
        # 处理描述文本
        description = repo.get('description') or '无描述'
        if len(description) > 100:
            description = description[:100] + "..."
        print(f"📝 描述: {description}")
        
        print(f"⭐ 星标数: {repo['stargazers_count']}")
        
        # 处理语言显示
        language = repo['language'] or '未识别'
        print(f"💻 编程语言: {language}")
        
        # 格式化日期
        for date_type in ['created_at', 'updated_at']:
            date_str = repo.get(date_type)
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    label = "创建时间" if date_type == 'created_at' else "更新时间"
                    print(f"📅 {label}: {dt.strftime('%Y年%m月%d日')}")
                except ValueError:
                    print(f"📅 {label}: {date_str}")
        
        print("-" * 50)
    
    # 打印语言分布（按项目数量降序排序）
    print("\n编程语言分布:")
    sorted_stats = sorted(analysis_result['language_stats'].items(), 
                         key=lambda x: x[1], reverse=True)
    for lang, count in sorted_stats:
        lang_display = lang if lang else "N/A"
        print(f"  {lang_display}: {count} 个项目")
    
    # 打印总结
    print(f"\n⭐ 总星标数: {analysis_result['total_stars']}")
    print(f"🍴 总Fork数: {analysis_result['total_forks']}")
    print(separator)

def save_markdown_report(repos: List[Dict], analysis_result: Dict, days: int = 7, filename: Optional[str] = None) -> str:
    """
    将分析结果保存为Markdown格式的报告
    
    Args:
        repos: 项目数据列表
        analysis_result: 分析结果字典
        days: 查询天数
        filename: 输出文件名（可选）
        
    Returns:
        生成的报告文件路径
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    if not filename:
        filename = f"github_trending_{days}days_{today_str}.md"
    query_time = datetime.now().strftime('%Y年%m月%d日')
    
    # 检查环境变量
    github_token = os.getenv("GITHUB_TOKEN")
    ai_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not github_token:
        print("⚠️ 警告：未检测到GITHUB_TOKEN环境变量，可能影响README获取")
    
    # 添加AI分析摘要
    repos = enrich_repos_with_ai_summaries(repos, github_token, ai_api_key)
    
    # 构建项目表格
    table_header = "| 排名 | 📦 项目名称 | 👤 作者 | ⭐ Star | 🍴 Fork | 语言 | 📝 描述 |\n"
    table_separator = "|------|----------|------|--------|--------|------|------|\n"
    
    table_rows = []
    for i, repo in enumerate(repos, 1):
        # 项目基本信息
        name_link = f"[{repo['name']}]({repo['html_url']})"
        owner = repo.get('owner', {})
        author_name = owner.get('login', 'N/A')
        author_link = owner.get('html_url', '')
        author_md = f"[{author_name}]({author_link})" if author_link else author_name
        stars = f"⭐ {repo['stargazers_count']}"
        forks = f"🍴 {repo.get('forks_count', 0)}"
        language = repo['language'] or 'N/A'
        
        # 处理描述文本
        description = repo.get('description') or '无描述'
        description = description.replace('\n', ' ').replace('|', '｜')
        if len(description) > 50:
            description = description[:50] + "..."
        
        # 添加AI分析摘要
        formatted_ai_summary = repo['ai_summary'].replace('\n', '\n> ')
        ai_summary_md = f"<br>> 🤖 **AI小结**:\n> {formatted_ai_summary}"
        
        # 合并描述和AI分析
        description_with_ai = f"{description}{ai_summary_md}"
        
        # 添加表格行
        table_rows.append(f"| {i} | {name_link} | {author_md} | {stars} | {forks} | {language} | {description_with_ai} |")
    
    # 构建语言分布表格（按项目数量降序排序）
    sorted_stats = sorted(analysis_result['language_stats'].items(), 
                         key=lambda x: x[1], reverse=True)
    lang_table = [
        "| 语言 | 项目数量 |",
        "| :--- | :------- |",  # 左对齐
        *[f"| {lang if lang else 'N/A'} | {count}个项目 |" 
          for lang, count in sorted_stats]
    ]
    
    # 写入Markdown文件
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # 报告标题
            f.write("# 🔥 GitHub 热门项目洞察报告\n\n")
            f.write(f"**查询时间：** {query_time}  ")
            f.write(f"**时间范围：** 最近{days}天  ")
            f.write(f"**项目数量：** {len(repos)}个\n\n")
            
            # 项目排行榜
            f.write("## 🏆 热门项目排行榜\n\n")
            f.write(table_header)
            f.write(table_separator)
            f.write("\n".join(table_rows))
            f.write("\n\n")
            
            # 语言分布
            f.write("## 📊 编程语言分布\n\n")
            f.write("\n".join(lang_table))
            f.write("\n\n")
            
            # 总结
            f.write(f"⭐ 总星标数: {analysis_result['total_stars']}  ")
            f.write(f"🍴 总Fork数: {analysis_result['total_forks']}\n")
            f.write("\n> 注：N/A 表示该项目未指定主语言，或为文档/多语言项目。\n")
        
        print(f"✅ Markdown报告已保存: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 保存Markdown报告失败: {e}")
        return ""

# 创建README缓存目录
README_CACHE_DIR = "readme_cache"
if not os.path.exists(README_CACHE_DIR):
    os.makedirs(README_CACHE_DIR)

def enrich_repos_with_ai_summaries(repos: List[Dict], github_token: Optional[str], ai_api_key: Optional[str]) -> List[Dict]:
    """
    为每个仓库添加AI生成的摘要
    
    Args:
        repos: 仓库列表
        github_token: GitHub API令牌
        ai_api_key: DeepSeek API密钥
        
    Returns:
        添加了ai_summary字段的仓库列表
    """
    # 检查API密钥
    if not ai_api_key:
        print("⚠️ 未检测到AI API Key，跳过AI总结")
        for repo in repos:
            repo['ai_summary'] = "AI总结功能未配置。"
        return repos
    
    print(f"⏳ 开始为 {len(repos)} 个项目生成AI分析摘要...")
    
    # 使用进度条处理每个仓库
    for repo in tqdm(repos, desc="生成AI总结"):
        # 获取README内容
        readme_content = get_readme_content(repo['full_name'], github_token)
        
        if readme_content:
            # 生成AI摘要
            repo['ai_summary'] = summarize_with_ai(readme_content, ai_api_key, repo)
        else:
            repo['ai_summary'] = "未能获取README内容。"
    
    return repos

def get_readme_content(repo_full_name: str, token: Optional[str]) -> Optional[str]:
    """
    获取仓库的README内容（带缓存机制）
    
    Args:
        repo_full_name: 仓库全名（owner/repo）
        token: GitHub API令牌
        
    Returns:
        README内容字符串，获取失败返回None
    """
    # 创建安全的缓存文件名
    cache_filename = f"{repo_full_name.replace('/', '__')}.md"
    cache_path = os.path.join(README_CACHE_DIR, cache_filename)
    
    # 检查缓存是否存在且有效（7天内）
    if os.path.exists(cache_path):
        cache_age = time.time() - os.path.getmtime(cache_path)
        if cache_age < 60 * 60 * 24 * 7:  # 7天有效期
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"⚠️ 读取缓存失败: {e}")
        else:
            print(f"♻️ 缓存已过期: {cache_filename}")
    
    # 没有有效缓存，从GitHub API获取
    if not token:
        print(f"⚠️ 缺少GitHub token，无法获取 {repo_full_name} 的README")
        return None
    
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content_base64 = response.json().get('content', '')
        decoded_content = base64.b64decode(content_base64).decode('utf-8')
        
        # 保存到缓存
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(decoded_content)
        except Exception as e:
            print(f"⚠️ 保存缓存失败: {e}")
            
        return decoded_content
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取README失败: {e}")
        return None

def summarize_with_ai(content: str, api_key: str, repo: Dict) -> str:
    """
    使用DeepSeek API生成项目摘要
    
    Args:
        content: README内容
        api_key: DeepSeek API密钥
        repo: 仓库信息字典
        
    Returns:
        AI生成的摘要字符串
    """
    # 添加API请求间隔防止速率限制
    time.sleep(1.2)
    
    # 显示处理进度
    content_size = len(content) / 1024  # KB
    print(f"  - 分析: {repo['name']} ({content_size:.1f}KB)")
    
    # 截断过长的内容
    if len(content) > 12000:
        content = content[:12000] + "...[内容截断]"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建分析提示
        prompt = f"""
作为GitHub趋势分析专家，请分析以下项目：

项目信息：
- 名称：{repo['name']}
- 主要语言：{repo['language'] or '未指定'}
- 星标数：{repo['stargazers_count']}
- 描述：{repo.get('description', '无')}

README内容：
{content}

请从以下3个方面分析：
1. 🎯 核心功能与解决的问题
2. 💡 技术亮点与创新点
3. 🔥 近期关注度高的原因

要求：
- 每点用"- "开头
- 每点不超过40字
- 使用专业但简洁的技术语言
"""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.3  # 降低随机性
        }
        
        # 发送API请求
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # 提取AI响应
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"❌ API请求失败: {e}")
        return "AI分析请求失败"
    except (KeyError, ValueError) as e:
        print(f"❌ 解析API响应失败: {e}")
        return "解析AI响应失败"

def save_raw_data(repos: List[Dict], filename: str = "trending_repos.json"):
    """
    保存原始项目数据到JSON文件
    
    Args:
        repos: 项目数据列表
        filename: 输出文件名
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(repos, f, ensure_ascii=False, indent=2)
        print(f"✅ 原始数据已保存: {filename}")
    except Exception as e:
        print(f"❌ 保存原始数据失败: {e}")

def compare_trends(previous_analysis: Dict, current_analysis: Dict, 
                  previous_repos: List[Dict], current_repos: List[Dict]):
    """
    对比两次趋势分析结果，生成变化报告
    
    Args:
        previous_analysis: 历史分析结果
        current_analysis: 当前分析结果
        previous_repos: 历史项目列表
        current_repos: 当前项目列表
    """
    # 报告头部
    header = "📈 GitHub趋势变化分析报告"
    separator = "=" * len(header)
    print(f"\n{separator}\n{header}\n{separator}")

    # 宏观指标对比
    def format_change(prev, curr, label):
        change = curr - prev
        pct_change = (change / prev * 100) if prev != 0 else float('inf')
        pct_str = f"{pct_change:+.2f}%" if prev != 0 else "N/A"
        print(f"{label}: {prev} → {curr} (变化: {change:+d}, {pct_str})")
    
    format_change(previous_analysis['total_stars'], current_analysis['total_stars'], "⭐ 总星标数")
    format_change(previous_analysis['total_forks'], current_analysis['total_forks'], "🍴 总Fork数")
    
    # 语言热度变化
    print("\n💻 编程语言热度变化:")
    all_langs = set(previous_analysis['language_stats'].keys()) | set(current_analysis['language_stats'].keys())
    
    for lang in sorted(all_langs):
        prev_count = previous_analysis['language_stats'].get(lang, 0)
        curr_count = current_analysis['language_stats'].get(lang, 0)
        if prev_count != curr_count:
            change = curr_count - prev_count
            pct_change = (change / prev_count * 100) if prev_count != 0 else float('inf')
            pct_str = f"{pct_change:+.2f}%" if prev_count != 0 else "N/A"
            print(f"  - {lang}: {prev_count} → {curr_count} (变化: {change:+d}, {pct_str})")

    # 3. 项目排名变化
    # 创建历史项目字典（包含排名和星标数）
    prev_dict = {}
    for i, repo in enumerate(previous_repos, 1):
        prev_dict[repo['full_name']] = {
            'rank': i,
            'stars': repo['stargazers_count']
        }
    
    curr_dict = {}
    for i, repo in enumerate(current_repos, 1):
        curr_dict[repo['full_name']] = {
            'rank': i,
            'stars': repo['stargazers_count']
        }
    
    # 新上榜项目
    new_projects = [repo for repo in current_repos if repo['full_name'] not in prev_dict]
    if new_projects:
        print(f"\n🆕 新上榜项目 ({len(new_projects)}个):")
        for repo in new_projects:
            print(f"  #{curr_dict[repo['full_name']]['rank']} {repo['name']} ⭐{repo['stargazers_count']}")
    
    # 排名变化项目
    rank_changes = []
    for repo in current_repos:
        name = repo['full_name']
        if name in prev_dict:
            prev_rank = prev_dict[name]['rank']
            curr_rank = curr_dict[name]['rank']
            if prev_rank != curr_rank:
                change = prev_rank - curr_rank
                # 添加历史星标数用于计算变化率
                repo['prev_stars'] = prev_dict[name]['stars']
                rank_changes.append((repo, prev_rank, curr_rank, change))
    
    if rank_changes:
        print(f"\n📊 排名变化 ({len(rank_changes)}个):")
        # 按变化幅度从大到小排序
        for repo, prev_rank, curr_rank, change in sorted(rank_changes, key=lambda x: abs(x[3]), reverse=True):
            direction = "📈" if change > 0 else "📉"  # 正变化表示排名上升
            # 计算星标数变化率（相对于历史星标数）
            star_change = repo['stargazers_count'] - repo['prev_stars']
            star_pct = (star_change / repo['prev_stars'] * 100) if repo['prev_stars'] != 0 else float('inf')
            star_pct_str = f"{star_pct:+.2f}%" if repo['prev_stars'] != 0 else "N/A"
            print(f"  {direction} {repo['name']}: #{prev_rank} → #{curr_rank} (排名变化: {change:+d}, 星标变化率: {star_pct_str})")

    print("=" * 50)

def find_comparison_file(days_ago: int, data_dir: str = 'data') -> Optional[str]:
    """
    查找与指定天数最匹配的历史数据文件
    
    Args:
        days_ago: 要对比的天数（如7表示7天前）
        data_dir: 数据文件目录
        
    Returns:
        最匹配的文件路径，找不到返回None
    """
    target_date = datetime.now() - timedelta(days=days_ago)
    pattern = os.path.join(data_dir, "data_*.json")
    files = glob.glob(pattern)
    
    if not files:
        return None

    # 查找日期最接近的文件
    closest_file = None
    min_diff = float('inf')
    
    for file_path in files:
        try:
            # 从文件名提取日期
            filename = os.path.basename(file_path)
            date_str = filename[5:-5]  # 提取"data_YYYY-MM-DD.json"中的日期部分
            file_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # 计算日期差
            date_diff = abs((target_date - file_date).days)
            
            # 更新最接近的文件
            if date_diff < min_diff:
                min_diff = date_diff
                closest_file = file_path
        except ValueError:
            continue  # 跳过格式不正确的文件名
    
    # 只返回日期差在2天内的文件
    return closest_file if min_diff <= 2 else None

def main():
    """主函数，协调整个分析流程"""
    # 检查GitHub令牌
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ 未检测到GITHUB_TOKEN环境变量，请检查设置！")
        return
    
    # 检查DeepSeek API密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️ 注意：未检测到DEEPSEEK_API_KEY环境变量，AI总结功能将不可用")
        print("   设置方法:")
        print('   Windows: $env:DEEPSEEK_API_KEY="your_api_key"')
        print('   Linux/macOS: export DEEPSEEK_API_KEY="your_api_key"')
    
    # 程序标题
    title = "🔥 GitHub热门项目洞察机器人"
    print(f"\n{title}\n{'=' * len(title)}")
    
    # 获取用户输入
    try:
        days_input = input("请输入查询天数 (默认7天): ").strip()
        days = int(days_input) if days_input.isdigit() else 7
        
        limit_input = input("请输入项目数量 (默认10个): ").strip()
        limit = int(limit_input) if limit_input.isdigit() else 10
    except ValueError:
        print("⚠️ 输入无效，使用默认值")
        days, limit = 7, 10
    
    print(f"\n🔄 获取最近{days}天的Top {limit}热门项目...")
    
    # 获取并分析数据
    repos = get_trending_repos(days=days, limit=limit, token=token)
    if not repos:
        print("⚠️ 未获取到热门项目，程序终止")
        return
    
    analysis_result = analyze_data(repos)
    
    # 准备目录结构
    data_dir = 'data'
    reports_dir = 'reports'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # 保存原始数据
    today_str = datetime.now().strftime('%Y-%m-%d')
    raw_data_path = os.path.join(data_dir, f"data_{today_str}.json")
    save_raw_data(repos, filename=raw_data_path)
    
    # 生成并保存报告
    print_console_report(repos, analysis_result)
    report_filename = os.path.join(reports_dir, f"github_trending_{days}days_{today_str}.md")
    save_markdown_report(repos, analysis_result, days=days, filename=report_filename)
    
    # 趋势对比分析
    print("\n📊 正在分析趋势变化...")
    try:
        comparison_file = find_comparison_file(days, data_dir)
        if comparison_file:
            print(f"🔍 找到对比文件: {comparison_file}")
            with open(comparison_file, 'r', encoding='utf-8') as f:
                previous_data = json.load(f)
            
            previous_analysis = analyze_data(previous_data)
            compare_trends(previous_analysis, analysis_result, previous_data, repos)
        else:
            print("ℹ️ 未找到合适的历史数据进行对比")
    except Exception as e:
        print(f"❌ 趋势分析失败: {e}")

if __name__ == "__main__":
    main()
