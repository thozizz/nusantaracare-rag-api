from app.services.parser import parse_document
import json

filepath = "data/raw_docs/nusantaracare_panduan_operasional_internal_v2.md"
doc_meta, chunks = parse_document(filepath)

print(f"Doc Title: {doc_meta.get('doc_title')}")
print(f"Doc Version: {doc_meta.get('doc_version')}")
print(f"Jumlah chunk: {len(chunks)}")

# Tampilkan 3 chunk pertama
for c in chunks[:3]:
    print(f"\nChunk ID: {c['chunk_id']}")
    print(f"Section: {c['section_title']}")
    print(f"Active: {c['metadata']['is_active']}")
    print(f"Preview: {c['text'][:150]}...")