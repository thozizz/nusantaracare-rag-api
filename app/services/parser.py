import re
import yaml
from typing import Dict, List, Any, Tuple

def parse_document(filepath: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Parsing dokumen markdown NusantaraCare.

    Args:
        filepath (str): Path menuju file .md

    Returns:
        Tuple[doc_metadata, list_of_chunks]
        - doc_metadata: dict dari frontmatter YAML
        - list_of_chunks: list of dict dengan keys:
            chunk_id, section_title, text, metadata (dict)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Ekstrak frontmatter (--- ... ---)
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        doc_metadata = yaml.safe_load(frontmatter_text)
        # Hapus frontmatter dari content
        content = content[frontmatter_match.end():]
    else:
        doc_metadata = {}

    # 2. Split konten berdasarkan heading level 2 (## ) atau level 1 (# ) 
    #    Kita akan potong per section dengan heading ## atau #
    #    Gunakan regex: split pada baris yang dimulai dengan # atau ## atau ###
    #    Strategi: split dengan lookahead positif: (?=^#)
    sections = re.split(r'\n(?=#+\s)', content.strip())

    chunks = []
    chunk_counter = 1

    # Kata kunci untuk mendeteksi bagian arsip nonaktif (v1.4)
    arsip_keywords = ["Arsip Kebijakan v1.4", "NONAKTIF", "v1.4", "versi 1.4"]

    for sec in sections:
        if not sec.strip():
            continue
        lines = sec.strip().split('\n')
        # Ambil heading pertama sebagai section_title
        heading_line = lines[0]
        # Hilangkan tanda # dan spasi
        section_title = heading_line.lstrip('#').strip()
        # Ambil body (sisanya)
        body = '\n'.join(lines[1:]).strip()
        if not body:
            # Jika tidak ada body, lewati
            continue

        # Tentukan apakah section ini adalah arsip nonaktif
        is_active = True
        # Cek apakah section_title atau body mengandung keyword arsip
        combined_text = (section_title + ' ' + body).lower()
        for kw in arsip_keywords:
            if kw.lower() in combined_text:
                is_active = False
                break
        # Juga periksa secara eksplisit jika section_title mengandung "Arsip" dan "v1.4"
        if "arsip kebijakan v1.4" in section_title.lower():
            is_active = False

        # Buat chunk_id
        doc_id = doc_metadata.get('doc_id', 'NC-OPS-001')
        chunk_id = f"{doc_id}#chunk-{chunk_counter:03d}"
        chunk_counter += 1

        # Metadata per chunk (ambil dari doc_metadata + tambahan)
        chunk_metadata = {
            "doc_id": doc_id,
            "doc_title": doc_metadata.get("doc_title"),
            "doc_version": doc_metadata.get("doc_version"),
            "category": doc_metadata.get("category"),
            "effective_date": doc_metadata.get("effective_date"),
            "is_active": is_active,  # Berdasarkan deteksi
            "source_path": doc_metadata.get("source_path"),
            "section_title": section_title,
        }
        chunks.append({
            "chunk_id": chunk_id,
            "section_title": section_title,
            "text": body,
            "metadata": chunk_metadata
        })

    return doc_metadata, chunks