#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电视猫(tvmao.com)分集剧情抓取工具

功能：
- 按剧名搜索并抓取分集剧情
- 使用剧集ID直接抓取
- 自动识别分集列表和剧情正文
- 按剧名目录与集数保存到本地
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote, unquote

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("请安装依赖: pip install requests beautifulsoup4")
    sys.exit(1)


class TVMaoScraper:
    """电视猫剧情抓取器"""
    
    BASE_URL = "https://www.tvmao.com"
    
    def __init__(self, output_dir: str = "./episodes", delay: float = 1.0):
        """
        初始化抓取器
        
        Args:
            output_dir: 输出目录
            delay: 请求延迟（秒）
        """
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        })
        
    def search_drama(self, keyword: str) -> List[Dict]:
        """
        搜索剧集
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            搜索结果列表 [{id, title, url, year, type}, ...]
        """
        print(f"正在搜索: {keyword}")
        
        url = f"{self.BASE_URL}/query.jsp"
        params = {'keys': keyword}
        
        try:
            resp = self.session.get(url, params=params, allow_redirects=False)
            
            # 检查是否重定向到剧集页面
            if resp.status_code == 302:
                location = resp.headers.get('Location', '')
                if '/drama/' in location:
                    # 直接跳转到剧集页面，提取ID
                    match = re.search(r'/drama/([^/]+)', location)
                    if match:
                        drama_id = match.group(1)
                        # 获取剧名
                        time.sleep(self.delay)
                        drama_url = f"{self.BASE_URL}/drama/{drama_id}"
                        detail_resp = self.session.get(drama_url)
                        soup = BeautifulSoup(detail_resp.text, 'html.parser')
                        title_tag = soup.select_one('strong.font24')
                        title = title_tag.get_text(strip=True) if title_tag else drama_id
                        return [{'id': drama_id, 'title': title, 'url': drama_url}]
            
            # 解析搜索结果页面
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                results = []
                
                # 查找搜索结果
                items = soup.select('.search-result-item, .result-item, ul.drama-list li')
                for item in items:
                    link = item.select_one('a')
                    if link and '/drama/' in link.get('href', ''):
                        href = link['href']
                        match = re.search(r'/drama/([^/]+)', href)
                        if match:
                            drama_id = match.group(1)
                            title = link.get_text(strip=True)
                            url = f"{self.BASE_URL}{href}"
                            
                            # 尝试提取年份和类型
                            info_text = item.get_text()
                            year_match = re.search(r'(\d{4})年', info_text)
                            year = year_match.group(1) if year_match else ''
                            
                            results.append({
                                'id': drama_id,
                                'title': title,
                                'url': url,
                                'year': year
                            })
                
                return results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            
        return []
    
    def get_episode_list(self, drama_id: str) -> Tuple[str, List[Dict]]:
        """
        获取分集列表
        
        Args:
            drama_id: 剧集ID
            
        Returns:
            (剧名, [{episode, url, title}, ...])
        """
        url = f"{self.BASE_URL}/drama/{drama_id}/episode"
        print(f"正在获取分集列表: {url}")
        
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 提取剧名
            title_tag = soup.select_one('strong.font24')
            drama_name = title_tag.get_text(strip=True) if title_tag else drama_id
            
            # 提取分集列表
            episodes = []
            episode_links = soup.select('.epipage li a')
            
            for link in episode_links:
                href = link.get('href', '')
                episode_num = link.get_text(strip=True)
                
                # 构建完整URL
                if href.startswith('/'):
                    episode_url = f"{self.BASE_URL}{href}"
                else:
                    episode_url = f"{self.BASE_URL}/drama/{drama_id}/episode/{href}"
                
                episodes.append({
                    'episode': episode_num,
                    'url': episode_url,
                    'title': ''
                })
            
            print(f"找到 {len(episodes)} 集")
            return drama_name, episodes
            
        except Exception as e:
            print(f"获取分集列表失败: {e}")
            return '', []
    
    def get_episode_content(self, url: str) -> Dict:
        """
        获取单集剧情内容
        
        Args:
            url: 分集URL
            
        Returns:
            {title, content, time}
        """
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 提取标题
            title_tag = soup.select_one('p.epi_t')
            title = title_tag.get_text(strip=True) if title_tag else ''
            
            # 提取时间
            time_tag = soup.select_one('.e_a_t p')
            time_text = ''
            if time_tag:
                time_text = time_tag.get_text(strip=True)
            
            # 提取正文
            content_parts = []
            article = soup.select_one('article.epi_c')
            
            if article:
                # 提取所有段落
                paragraphs = article.select('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # 过滤掉版权声明等无关内容
                    if text and '电视猫' not in text and '未经许可' not in text and '转载许可' not in text:
                        content_parts.append(text)
            
            content = '\n\n'.join(content_parts)
            
            return {
                'title': title,
                'content': content,
                'time': time_text
            }
            
        except Exception as e:
            print(f"获取剧情失败 ({url}): {e}")
            return {'title': '', 'content': '', 'time': ''}
    
    def save_episode(self, drama_name: str, episode_num: str, 
                     title: str, content: str, time_text: str = '',
                     fmt: str = 'txt') -> Path:
        """
        保存单集剧情
        
        Args:
            drama_name: 剧名
            episode_num: 集数
            title: 标题
            content: 正文
            time_text: 时间
            fmt: 格式（txt/markdown）
            
        Returns:
            保存的文件路径
        """
        # 创建目录
        safe_name = self._sanitize_filename(drama_name)
        drama_dir = self.output_dir / safe_name
        drama_dir.mkdir(parents=True, exist_ok=True)
        
        # 格式化文件名
        episode_str = episode_num.zfill(2) if episode_num.isdigit() else episode_num
        filename = f"第{episode_str}集.{fmt}"
        filepath = drama_dir / filename
        
        # 格式化内容
        if fmt == 'markdown' or fmt == 'md':
            file_content = self._format_markdown(drama_name, episode_num, title, content, time_text)
        else:
            file_content = self._format_text(drama_name, episode_num, title, content, time_text)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"已保存: {filepath}")
        return filepath
    
    def _format_text(self, drama_name: str, episode_num: str,
                     title: str, content: str, time_text: str) -> str:
        """格式化为纯文本"""
        lines = []
        lines.append(f"{drama_name} 第{episode_num}集")
        if title:
            lines.append(f"标题：{title}")
        if time_text:
            lines.append(f"时间：{time_text}")
        lines.append("")
        lines.append(content)
        return '\n'.join(lines)
    
    def _format_markdown(self, drama_name: str, episode_num: str,
                         title: str, content: str, time_text: str) -> str:
        """格式化为Markdown"""
        lines = []
        lines.append(f"# {drama_name} 第{episode_num}集")
        lines.append("")
        if title:
            lines.append(f"## {title}")
            lines.append("")
        if time_text:
            lines.append(f"> 时间：{time_text}")
            lines.append("")
        lines.append(content)
        return '\n'.join(lines)
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名中的非法字符"""
        # 替换Windows文件名非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        return re.sub(illegal_chars, '_', name).strip()
    
    def scrape_all(self, drama_id: str, start: int = 1, 
                   end: Optional[int] = None, fmt: str = 'txt') -> List[Path]:
        """
        抓取所有分集剧情
        
        Args:
            drama_id: 剧集ID
            start: 起始集数
            end: 结束集数（None表示全部）
            fmt: 输出格式
            
        Returns:
            保存的文件路径列表
        """
        # 获取分集列表
        drama_name, episodes = self.get_episode_list(drama_id)
        
        if not episodes:
            print("未找到分集")
            return []
        
        saved_files = []
        
        # 确定抓取范围
        total = len(episodes)
        if end is None or end > total:
            end = total
        
        print(f"\n开始抓取 {drama_name} 第{start}-{end}集（共{total}集）\n")
        
        for i, ep in enumerate(episodes):
            ep_num = i + 1
            
            # 检查范围
            if ep_num < start:
                continue
            if ep_num > end:
                break
            
            print(f"正在抓取第{ep_num}集...")
            
            # 获取内容
            content_data = self.get_episode_content(ep['url'])
            
            # 保存
            filepath = self.save_episode(
                drama_name=drama_name,
                episode_num=str(ep_num),
                title=content_data['title'],
                content=content_data['content'],
                time_text=content_data['time'],
                fmt=fmt
            )
            saved_files.append(filepath)
            
            # 延迟
            if i < len(episodes) - 1:
                time.sleep(self.delay)
        
        print(f"\n完成！共保存 {len(saved_files)} 集到 {self.output_dir / drama_name}")
        return saved_files
    
    def scrape_episode(self, drama_id: str, episode: int, fmt: str = 'txt') -> Optional[Path]:
        """
        抓取单集剧情
        
        Args:
            drama_id: 剧集ID
            episode: 集数
            fmt: 输出格式
            
        Returns:
            保存的文件路径
        """
        # 获取分集列表
        drama_name, episodes = self.get_episode_list(drama_id)
        
        if not episodes:
            print("未找到分集")
            return None
        
        if episode < 1 or episode > len(episodes):
            print(f"集数超出范围（1-{len(episodes)}）")
            return None
        
        # 获取指定集内容
        ep = episodes[episode - 1]
        print(f"正在抓取第{episode}集...")
        
        content_data = self.get_episode_content(ep['url'])
        
        # 保存
        filepath = self.save_episode(
            drama_name=drama_name,
            episode_num=str(episode),
            title=content_data['title'],
            content=content_data['content'],
            time_text=content_data['time'],
            fmt=fmt
        )
        
        return filepath


def main():
    parser = argparse.ArgumentParser(
        description='电视猫(tvmao.com)分集剧情抓取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 搜索剧名并抓取全部
  python tvmao_scraper.py --search "神盾局特工"
  
  # 使用剧集ID抓取全部
  python tvmao_scraper.py --id ai4vJS8=
  
  # 抓取单集
  python tvmao_scraper.py --id ai4vJS8= --episode 1
  
  # 抓取指定范围
  python tvmao_scraper.py --id ai4vJS8= --start 1 --end 10
  
  # 指定输出目录和格式
  python tvmao_scraper.py --id ai4vJS8= --output ./剧情 --format markdown
        """
    )
    
    # 搜索或ID（二选一）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--search', '-s', help='按剧名搜索')
    group.add_argument('--id', '-i', help='指定剧集ID')
    
    # 集数选项
    parser.add_argument('--episode', '-e', type=int, help='抓取指定集数')
    parser.add_argument('--start', type=int, default=1, help='起始集数（默认：1）')
    parser.add_argument('--end', type=int, help='结束集数')
    
    # 输出选项
    parser.add_argument('--output', '-o', default='./episodes', help='输出目录（默认：./episodes）')
    parser.add_argument('--format', '-f', choices=['txt', 'markdown', 'md'], 
                        default='txt', help='输出格式（默认：txt）')
    
    # 其他选项
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='请求延迟秒数（默认：1.0）')
    
    args = parser.parse_args()
    
    # 创建抓取器
    scraper = TVMaoScraper(output_dir=args.output, delay=args.delay)
    
    # 确定剧集ID
    drama_id = args.id
    
    if args.search:
        # 搜索剧名
        results = scraper.search_drama(args.search)
        
        if not results:
            print("未找到相关剧集")
            sys.exit(1)
        
        if len(results) == 1:
            # 只有一个结果，直接使用
            drama_id = results[0]['id']
            print(f"找到剧集: {results[0]['title']}")
        else:
            # 多个结果，让用户选择
            print("\n找到以下剧集:")
            for i, r in enumerate(results[:10], 1):  # 只显示前10个
                print(f"  {i}. {r['title']} {r.get('year', '')} - {r['id']}")
            
            if len(results) > 10:
                print(f"  ... 还有 {len(results) - 10} 个结果")
            
            print("\n请选择序号（1-{0}），或按Enter取消：".format(min(len(results), 10)))
            try:
                choice = input("> ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        drama_id = results[idx]['id']
                        print(f"已选择: {results[idx]['title']}")
            except (ValueError, KeyboardInterrupt):
                print("已取消")
                sys.exit(0)
    
    if not drama_id:
        print("无法确定剧集ID")
        sys.exit(1)
    
    # 执行抓取
    if args.episode:
        # 单集
        scraper.scrape_episode(drama_id, args.episode, args.format)
    else:
        # 全部或范围
        scraper.scrape_all(drama_id, args.start, args.end, args.format)


if __name__ == '__main__':
    main()
