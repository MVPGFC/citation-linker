#!/usr/bin/env python3
"""
academic_citation_linker.py
基于 OpenAlex API 的学术论文引用关联工具。
无需 API key，完全免费。

用法:
  Step 1: 提取引用
    python3 academic_citation_linker.py --extract "<文本>"

  Step 2: 搜索/获取数据
    Agent 需根据自身环境选择工具访问生成的 URL：
    - 首选：MCP 工具 `extract_content_from_websites`
    - 备选：通用 `WebSearch`、`Browser` 或任何能读取 URL 内容的工具
    
    访问地址:
    https://api.openalex.org/works?filter=title_and_abstract.search:<英文词>&per_page=35

  Step 3: 格式化输出
    cat results.json | python3 academic_citation_linker.py --format "<文本>"
"""

import sys
import json
import re
import argparse
import urllib.parse

# ─────────────────────────────────────────
# 1. 提取引用
# ─────────────────────────────────────────
CHINESE_STOPWORDS = {
    '的', '了', '是', '在', '和', '与', '或', '等', '及', '为', '以', '对', '于',
    '中', '其', '而', '则', '将', '又', '但', '因', '被', '这', '那', '有', '个',
    '不', '也', '就', '要', '会', '能', '可', '所', '上', '下', '内', '外', '后',
    '前', '当', '从', '到', '把', '让', '给', '用', '通过', '根据', '按照', '关于',
    '一些', '这种', '那种', '本文', '该', '每', '各', '某', '本', '之', '与',
}

TERM_MAP = {
    # ── 岩石力学/采矿工程 ──
    '煤岩': 'coal rock', '冲击地压': 'rock burst', '失稳机理': 'instability mechanism',
    '裂纹扩展': 'crack propagation', '应变率': 'strain rate', '微裂隙': 'microcrack',
    '分形': 'fractal', '霍普金森压杆': 'Split Hopkinson pressure bar SHPB',
    '动力失稳': 'dynamic instability', '高地应力': 'high in-situ stress',
    '同步辐射': 'synchrotron radiation', 'CT技术': 'CT imaging dynamic',
    '渗流': 'seepage flow', '应力耦合': 'stress coupling', '能量释放率': 'energy release rate',
    '裂隙分形维数': 'fractal dimension fracture', 'SHPB实验': 'SHPB test Hopkinson',
    '岩石力学': 'rock mechanics', '深部开采': 'deep mining',
    '岩爆': 'rockburst', '煤与瓦斯突出': 'coal gas outburst',
    '断层': 'fault', '节理': 'joint', '黏土矿物': 'clay mineral',
    '剪切': 'shear', '压缩': 'compression', '拉伸': 'tension',
    '断裂': 'fracture', '裂纹分形': 'crack fractal', '应变率敏感': 'strain rate sensitivity',
    '动态': 'dynamic', '静态': 'static', '强度': 'strength',
    '破坏': 'failure', '韧性': 'toughness', '脆性': 'brittle',
    '弹性模量': 'elastic modulus', '泊松比': "Poisson's ratio",
    '深部': 'deep', '高渗压': 'high pore pressure',
    '耦合': 'coupling', '跨尺度': 'multi-scale', '定量': 'quantitative',
    '关联': 'correlation', '预测': 'prediction', '误差': 'error',
    '实验': 'experiment', '数值模拟': 'numerical simulation',
    '有限元': 'finite element', '离散元': 'discrete element',
    # ── 通用学术术语（适用任意学科） ──
    '神经网络': 'neural network', '深度学习': 'deep learning', '机器学习': 'machine learning',
    '人工智能': 'artificial intelligence', '大数据': 'big data',
    '气候变化': 'climate change', '全球变暖': 'global warming',
    '新冠': 'COVID-19', '疫苗': 'vaccine', '免疫': 'immune',
    '基因编辑': 'gene editing', 'CRISPR': 'CRISPR', '蛋白质': 'protein',
    '量子计算': 'quantum computing', '区块链': 'blockchain',
    '可持续发展': 'sustainable development', '碳中和': 'carbon neutral',
}

def extract_citations(text):
    """提取引用标识及上下文。"""
    matches = list(re.finditer(r'\[(\d+)\]', text))
    citations = []
    for i, match in enumerate(matches):
        cite_key = match.group(1)
        start_pos = match.start()
        prev_end = matches[i-1].end() if i > 0 else 0
        context = text[prev_end:start_pos].strip()
        if len(context) < 30 and prev_end > 0:
            ext = max(0, text.rfind('.', prev_end, start_pos))
            context = text[ext:start_pos].strip()
        citations.append({'key': cite_key, 'context': context, 'position': start_pos})
    return citations

def build_search_query(context):
    """中文关键词，去停用词。"""
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff\-\(\)]', ' ', context)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if len(cleaned) > 200:
        lp = max(cleaned.rfind('；'), cleaned.rfind(';'), cleaned.rfind('。'), cleaned.rfind('.'))
        if lp > len(cleaned) - 150:
            cleaned = cleaned[lp+1:]
        else:
            cleaned = cleaned[-180:]
    words = [w for w in cleaned.split() if len(w) > 1 and w not in CHINESE_STOPWORDS]
    return ' '.join(words[:12]) if len(words) >= 3 else cleaned

def translate_query(context):
    """中译英术语映射。"""
    result = context
    for cn, en in TERM_MAP.items():
        result = result.replace(cn, en)
    terms = re.findall(r'[a-zA-Z]{3,}', result)
    seen, out = set(), []
    for t in terms:
        if t not in seen: seen.add(t); out.append(t)
    return ' '.join(out) if out else result

def build_openalex_url(query_en, per_page=35):
    """构建 OpenAlex API URL。"""
    safe = urllib.parse.quote(query_en)
    return f"https://api.openalex.org/works?filter=title_and_abstract.search:{safe}&per_page={per_page}"

# ─────────────────────────────────────────
# 2. 解析 OpenAlex JSON 响应
# ─────────────────────────────────────────
def parse_openalex_response(text: str) -> list[dict]:
    """
    解析 OpenAlex API 返回的 JSON，提取论文关键字段。
    支持直接 JSON 或包装在 MCP 响应中的情况。
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    # 处理 MCP 包装格式
    if isinstance(data, dict):
        content = None
        if 'result' in data:
            r = data['result']
            if isinstance(r, dict) and 'content' in r:
                content = r['content']
            elif isinstance(r, str):
                content = r
        elif 'content' in data:
            content = data['content']
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    try:
                        data = json.loads(item['text'])
                        break
                    except Exception:
                        pass
        elif isinstance(content, str):
            try:
                data = json.loads(content)
            except Exception:
                return []

    if not isinstance(data, dict) or 'results' not in data:
        return []

    papers = []
    for w in data.get('results', []):
        authors = []
        for a in w.get('authorships', []):
            an = a.get('author', {})
            display = a.get('display_name', '')
            if display:
                authors.append(display)
            elif an.get('display_name'):
                authors.append(an['display_name'])

        locations = w.get('locations', [])
        doi = w.get('doi', '')
        url = doi
        pdf_url = ''
        
        # Try to find a direct PDF URL first, then fallback to landing page
        for loc in locations:
            if loc.get('pdf_url'):
                pdf_url = loc.get('pdf_url')
                url = pdf_url
                break
        
        if not pdf_url:
            for loc in locations:
                if loc.get('landing_page_url'):
                    url = loc.get('landing_page_url')
                    break
        
        open_access = w.get('open_access', {})
        is_oa = open_access.get('is_oa', False)
        oa_url = open_access.get('oa_url', '')
        
        if oa_url and not pdf_url:
            url = oa_url
            pdf_url = oa_url

        published = ''
        date = w.get('publication_date', '')
        if not date and w.get('publication_year'):
            published = str(w['publication_year'])
        elif date:
            published = date[:10] if len(date) >= 10 else date

        primary_loc = w.get('primary_location', {})
        source = primary_loc.get('source', {}) or {}
        journal = source.get('display_name', '')

        papers.append({
            'id': w.get('id', '').split('/')[-1] if w.get('id') else '',
            'title': w.get('title', '') or '',
            'authors': authors[:8],
            'published': published,
            'year': w.get('publication_year', ''),
            'journal': journal,
            'doi': doi,
            'url': url or doi,
            'pdf_url': pdf_url,
            'is_oa': is_oa,
            'abstract': w.get('abstract', '') or '',
            'cited_by': w.get('cited_by_count', 0),
            'topics': [t.get('display_name', '') for t in w.get('topics', [])[:4]],
        })
    return papers

# ─────────────────────────────────────────
# 3. 选优
# ─────────────────────────────────────────
def score_papers(papers: list[dict], context: str) -> int:
    en_terms = re.findall(r'[a-zA-Z]{4,}', context.lower())
    best_score, best_idx = -1, 0
    for idx, p in enumerate(papers):
        score = 0
        tl = p['title'].lower()
        al = (p.get('abstract') or '').lower()
        jl = (p.get('journal') or '').lower()
        for t in en_terms:
            if t in tl: score += 5
            if t in al: score += 2
            if t in jl: score += 1
        for num in re.findall(r'\d+(?:\.\d+)?', context):
            if num in tl or num in al: score += 1
        if re.match(r'^[A-Za-z]', p['title'].strip()): score += 3
        score += min(p.get('cited_by', 0) * 0.01, 5)
        if score > best_score:
            best_score, best_idx = score, idx
    return best_idx

# ─────────────────────────────────────────
# 4. 格式化
# ─────────────────────────────────────────
def format_paper(p: dict, key: str, fmt='text') -> str:
    authors = p.get('authors', [])
    ad = ', '.join(authors[:5])
    if len(authors) > 5: ad += f' et al. (+{len(authors)-5})'
    year = p.get('year') or (p['published'][:4] if p.get('published') else 'N/A')

    data = {
        'cite_key': f'[{key}]',
        'paper_id': p.get('id', ''),
        'title': p['title'],
        'authors': authors,
        'author_display': ad,
        'year': year,
        'journal': p.get('journal', ''),
        'doi': p.get('doi', ''),
        'url': p.get('url', ''),
        'pdf_url': p.get('pdf_url', ''),
        'is_oa': p.get('is_oa', False),
        'cited_by': p.get('cited_by', 0),
        'abstract': (p.get('abstract') or '')[:500],
        'topics': p.get('topics', [])[:4],
    }
    if fmt == 'json':
        return json.dumps(data, ensure_ascii=False, indent=2)
    topics = ', '.join(data['topics']) if data['topics'] else 'N/A'
    cited = f"{data['cited_by']} 次引用" if data['cited_by'] else '无引用数据'
    oa_status = "✅ 免费开源" if data['is_oa'] else "🔒 付费/未知"
    
    return '\n'.join([
        f"[{key}] → {data['paper_id'] or data['doi']}",
        f"标题: {data['title']}",
        f"作者: {ad}",
        f"年份: {year}",
        f"期刊: {data['journal'] or 'N/A'}",
        f"DOI: {data['doi'] or 'N/A'}",
        f"链接: {data['url'] or 'N/A'}",
        f"直达PDF: {data['pdf_url'] or '未提供'}",
        f"开源状态: {oa_status}",
        f"引用: {cited}",
        f"关键词: {topics}",
    ])

# ─────────────────────────────────────────
# 5. 主流程
# ─────────────────────────────────────────
def cmd_extract(text: str):
    """Step 1: 提取引用和 OpenAlex URL。"""
    cites = extract_citations(text)
    if not cites:
        print("错误: 未找到 [数字] 格式的引用标识", file=sys.stderr)
        sys.exit(1)
    results = []
    for c in cites:
        key = c['key']
        ctx = c['context']
        if not ctx: continue
        q_en = translate_query(ctx) or build_search_query(ctx)
        results.append({
            'cite_key': key,
            'context': ctx,
            'search_query_en': q_en,
            'openalex_url': build_openalex_url(q_en),
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))

def cmd_format(text: str, papers_by_key: dict, fmt='text'):
    """Step 3: 格式化输出。"""
    cites = extract_citations(text)
    all_out = []
    bibliography = []  # List to store formatted references
    
    for c in cites:
        key = c['key']
        ctx = c['context']
        if not ctx: continue
        papers = papers_by_key.get(key, [])
        if not papers:
            print(f"[{key}] 未找到匹配论文\n", file=sys.stderr)
            continue
        best_idx = score_papers(papers, ctx)
        best = papers[best_idx]
        
        # Format bibliography entry (IEEE style approximation)
        authors = best.get('authors', [])
        author_text = ', '.join(authors[:3])
        if len(authors) > 3:
            author_text += ' et al.'
        elif not authors:
            author_text = "Anon"
            
        title = best.get('title', 'Untitled')
        journal = best.get('journal', '')
        year = best.get('year') or (best.get('published', '')[:4]) or 'n.d.'
        doi = best.get('doi', '')
        
        # Standard format: [1] Author, "Title," Journal, Year. DOI
        bib_entry = f"[{key}] {author_text}, \"{title},\""
        if journal:
            bib_entry += f" {journal},"
        bib_entry += f" {year}."
        if doi:
            bib_entry += f" DOI: {doi}"
            
        bibliography.append(bib_entry)

        if fmt == 'json':
            all_out.append({
                'cite_key': f'[{key}]',
                'context': ctx,
                'papers_found': len(papers),
                'best_paper': {
                    'id': best.get('id', ''),
                    'title': best['title'],
                    'authors': best.get('authors', []),
                    'year': best.get('year', ''),
                    'journal': best.get('journal', ''),
                    'doi': best.get('doi', ''),
                    'url': best.get('url', ''),
                    'pdf_url': best.get('pdf_url', ''),
                    'is_oa': best.get('is_oa', False),
                    'cited_by': best.get('cited_by', 0),
                    'abstract': best.get('abstract', ''),
                    'topics': best.get('topics', []),
                }
            })
        else:
            print(f"\n{'='*60}")
            print(f"引用 [{key}] → 关联论文:")
            print(f"上下文: …{ctx[-100:]}…")
            print(f"找到 {len(papers)} 篇，选择最佳匹配:")
            print(format_paper(best, key, 'text'))
            
    if fmt == 'text' and bibliography:
        print(f"\n\n{'='*60}")
        print("参考文献列表 (Bibliography)")
        print(f"{'='*60}")
        for entry in bibliography:
            print(entry)
            
    if fmt == 'json':
        print(json.dumps(all_out, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description='学术论文引用关联工具（OpenAlex 版）')
    parser.add_argument('--extract', metavar='TEXT', help='提取引用，输出 JSON（含 OpenAlex URL）')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='格式化输出')
    parser.add_argument('text', nargs='?', help='原始文本（配合 --format 使用）')
    args = parser.parse_args()

    if args.extract:
        cmd_extract(args.extract)
    elif args.text:
        try:
            data = json.load(sys.stdin)
        except Exception:
            print("错误: 需要从 stdin 传入 papers JSON", file=sys.stderr)
            sys.exit(1)
        papers_by_key = {}
        for item in data:
            k = item.get('cite_key', '').strip().strip('[]')
            papers_by_key[k] = item.get('papers', [])
        cmd_format(args.text, papers_by_key, args.format)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
