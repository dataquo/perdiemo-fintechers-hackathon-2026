# -*- coding: utf-8 -*-
"""
export_notion_guides.py — Export complete hackathon Notion guides into Markdown.
"""
import urllib.request
import json
import os
from pathlib import Path

def get_complete_block_tree(page_id):
    url = 'https://www.notion.so/api/v3/loadCachedPageChunk'
    data = json.dumps({
        'page': {'id': page_id},
        'limit': 100,
        'cursor': {'stack': []},
        'chunkNumber': 0,
        'verticalColumns': False
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    })
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        blocks = res.get('recordMap', {}).get('block', {})

    while True:
        missing = set()
        for k, v in blocks.items():
            val = v.get('value', {})
            if 'value' in val:
                val = val['value']
            for cid in val.get('content', []):
                if cid not in blocks:
                    missing.add(cid)
        if not missing:
            break
        missing_list = list(missing)
        for i in range(0, len(missing_list), 100):
            batch = missing_list[i:i+100]
            sync_data = json.dumps({
                'requests': [{'pointer': {'table': 'block', 'id': cid}, 'version': -1} for cid in batch]
            }).encode('utf-8')
            sync_req = urllib.request.Request(
                'https://www.notion.so/api/v3/syncRecordValues',
                data=sync_data,
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(sync_req) as s_resp:
                s_res = json.loads(s_resp.read().decode('utf-8'))
                blocks.update(s_res.get('recordMap', {}).get('block', {}))
    return blocks

def format_title(title_chunks):
    if not title_chunks:
        return ''
    res = []
    for chunk in title_chunks:
        if not isinstance(chunk, list):
            continue
        text = chunk[0]
        if len(chunk) > 1 and isinstance(chunk[1], list):
            for mod in chunk[1]:
                if mod[0] == 'b':
                    text = f"**{text}**"
                elif mod[0] == 'i':
                    text = f"*{text}*"
                elif mod[0] == 'c':
                    text = f"`{text}`"
                elif mod[0] == 's':
                    text = f"~~{text}~~"
                elif mod[0] == 'a':
                    text = f"[{text}]({mod[1]})"
        res.append(text)
    return ''.join(res)

def block_to_md(block_id, blocks, depth=0):
    wrapper = blocks.get(block_id, {})
    val = wrapper.get('value', {})
    if 'value' in val:
        val = val['value']
    if not val:
        return []

    b_type = val.get('type', 'text')
    props = val.get('properties', {})
    title = format_title(props.get('title', []))
    content_ids = val.get('content', [])

    lines = []
    indent = '  ' * depth

    if b_type == 'page':
        if depth == 0:
            lines.append(f"# {title}\n")
        else:
            lines.append(f"\n### 📄 {title}\n")
    elif b_type == 'header':
        lines.append(f"\n## {title}\n")
    elif b_type == 'sub_header':
        lines.append(f"\n### {title}\n")
    elif b_type == 'sub_sub_header':
        lines.append(f"\n#### {title}\n")
    elif b_type == 'text':
        if title.strip():
            lines.append(f"{title}\n")
    elif b_type == 'bulleted_list':
        lines.append(f"{indent}- {title}")
    elif b_type == 'numbered_list':
        lines.append(f"{indent}1. {title}")
    elif b_type == 'to_do':
        checked = props.get('checked', [['No']])[0][0] == 'Yes'
        box = '[x]' if checked else '[ ]'
        lines.append(f"{indent}- {box} {title}")
    elif b_type == 'toggle':
        lines.append(f"\n<details><summary><b>{title}</b></summary>\n")
    elif b_type == 'code':
        lang = props.get('language', [['text']])[0][0].lower()
        lines.append(f"```{lang}\n{title}\n```\n")
    elif b_type == 'quote':
        lines.append(f"> {title}\n")
    elif b_type == 'callout':
        lines.append(f"> [!NOTE]\n> {title}\n")
    elif b_type == 'divider':
        lines.append("\n---\n")
    elif b_type == 'table_row':
        row_cells = []
        for prop_name, prop_val in sorted(props.items()):
            row_cells.append(format_title(prop_val))
        lines.append('| ' + ' | '.join(row_cells) + ' |')
    elif b_type == 'table':
        pass
    else:
        if title.strip():
            lines.append(f"{title}\n")

    # recurse into children
    child_depth = depth + 1 if b_type in ('bulleted_list', 'numbered_list') else depth
    for cid in content_ids:
        lines.extend(block_to_md(cid, blocks, child_depth))

    if b_type == 'toggle':
        lines.append("\n</details>\n")

    return lines

if __name__ == '__main__':
    out_dir = Path('docs/notion_guides')
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching AWS Participant Guide...")
    blocks_aws = get_complete_block_tree('3fd1e819-9813-81ea-a7c9-cfc078a6b2bb')
    md_aws = '\n'.join(block_to_md('3fd1e819-9813-81ea-a7c9-cfc078a6b2bb', blocks_aws))
    with open(out_dir / 'AWS_Participant_Guide.md', 'w', encoding='utf-8') as f:
        f.write(md_aws)
    print(f"Wrote AWS_Participant_Guide.md: {len(md_aws)} characters.")

    print("Fetching Hackers Guide...")
    blocks_hacker = get_complete_block_tree('3f41e819-9813-81cf-9981-d4d0e6f62eba')
    md_hacker = '\n'.join(block_to_md('3f41e819-9813-81cf-9981-d4d0e6f62eba', blocks_hacker))
    with open(out_dir / 'Hackers_Guide.md', 'w', encoding='utf-8') as f:
        f.write(md_hacker)
    print(f"Wrote Hackers_Guide.md: {len(md_hacker)} characters.")
