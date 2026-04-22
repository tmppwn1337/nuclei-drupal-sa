# nuclei-drupal-sa
Nuclei templates for drupal vulns... far from perfect

PR if you want stuff to change.

How to use
---
```
nuclei -t ./nuclei-drupal-sa/templates/ --target https://www.example.com
```

Path extraction helper
---
Generate `extracted-paths.txt` from repository file contents:

```
python3 extract_paths.py
```

Rules/limitations:
- Recursively reads repository files (excluding `.git` and the output file itself).
- Extracts path-like strings (URLs, absolute paths, and relative paths with `/` separators).
- De-duplicates and sorts extracted values.
- Uses regex-based extraction, so results are best-effort path-like matches from text content.
