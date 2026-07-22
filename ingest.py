import os
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from email import message_from_string

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Try importing python-frontmatter, fallback to manual if not installed yet
try:
    import frontmatter
except ImportError:
    frontmatter = None

class AuraIngestor:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.allowed_extensions = {'.txt', '.md'}

    def normalize_text(self, text: str) -> str:
        """Cleans whitespaces, normalizes line breaks, and strips tracking artifacts."""
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def parse_note(self, content: str, file_path: Path) -> dict:
        """Parses Markdown notes, extracting YAML frontmatter or falling back to file names."""
        title, author, date_str = None, None, None
        raw_text = content
        
        if frontmatter:
            try:
                post = frontmatter.loads(content)
                title = post.get('title')
                author = post.get('author')
                date_str = str(post.get('date')) if post.get('date') else None
                raw_text = post.content
            except Exception:
                raw_text = content
        else:
            # Fallback manual frontmatter extraction if package missing
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    raw_text = parts[2]
                    for line in parts[1].split('\n'):
                        if ':' in line:
                            k, v = line.split(':', 1)
                            k, v = k.strip().lower(), v.strip()
                            if k == 'title': title = v
                            elif k == 'author': author = v
                            elif k == 'date': date_str = v
                else:
                    raw_text = content
            else:
                raw_text = content

        # Fallback values if metadata isn't explicitly defined in frontmatter
        if not title:
            title = file_path.stem.replace('_', ' ').replace('-', ' ').title()

        return {
            "metadata": {
                "title": title,
                "author": author,
                "date": date_str
            },
            "body": raw_text
        }

    def parse_email(self, content: str) -> dict:
        """Parses plain text emails extracting From/To/Subject standard headers."""
        msg = message_from_string(content)
        
        # Extract headers safely
        author = msg.get('From')
        title = msg.get('Subject')
        date_raw = msg.get('Date')
        
        # Handle cases where email doesn't strictly adhere to standard header format
        if not author and not title and "From:" in content:
            lines = content.split('\n')
            for line in lines[:10]: # Look at top lines
                if line.startswith('From:'): author = line.replace('From:', '').strip()
                elif line.startswith('Subject:'): title = line.replace('Subject:', '').strip()
                elif line.startswith('Date:'): date_raw = line.replace('Date:', '').strip()
        
        # Extract clean body text
        if msg.is_multipart():
            body_parts = []
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_parts.append(payload.decode('utf-8', errors='ignore'))
            body = "\n".join(body_parts) if body_parts else content
        else:
            payload = msg.get_payload()
            body = payload if isinstance(payload, str) else content

        if not msg.keys() and "Subject:" in content:
            body = content.split('\n\n', 1)[-1] if '\n\n' in content else content

        return {
            "metadata": {
                "title": title if title else "Untitled Email",
                "author": author if author else None,
                "date": date_raw if date_raw else None
            },
            "body": body
        }

    def parse_document(self, content: str, file_path: Path) -> dict:
        """Parses standard plain text documents."""
        return {
            "metadata": {
                "title": file_path.stem.replace('_', ' ').replace('-', ' ').title(),
                "author": None,
                "date": None
            },
            "body": content
        }

    def process_file(self, file_path: Path, source_type: str) -> dict:
        """Transforms raw files into the common AURA-KG ingestion contract."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if source_type == 'note':
            parsed = self.parse_note(content, file_path)
        elif source_type == 'email':
            parsed = self.parse_email(content)
        elif source_type == 'document':
            parsed = self.parse_document(content, file_path)
        else:
            parsed = {"metadata": {"title": None, "author": None, "date": None}, "body": content}

        metadata = parsed["metadata"]
        raw_text = parsed["body"]

        try:
            rel_path = str(file_path.relative_to(self.data_dir.parent))
        except ValueError:
            rel_path = str(file_path)

        return {
            "source_type": source_type,
            "source_path": rel_path,
            "raw_text": self.normalize_text(raw_text),
            "metadata": metadata
        }

    def run_pipeline(self) -> list:
        """Scans the dummy folders, normalizes all files, and compiles the output payload."""
        normalized_dataset = []
        subfolders = {'notes': 'note', 'emails': 'email', 'documents': 'document'}

        print("🚀 Starting AURA-KG Data Ingestion Pipeline...")
        
        for folder_name, source_type in subfolders.items():
            target_dir = self.data_dir / folder_name
            if not target_dir.exists():
                print(f"⚠️ Warning: Subfolder '{folder_name}' not found in {self.data_dir}")
                continue

            for file in target_dir.iterdir():
                if file.is_file() and file.suffix in self.allowed_extensions:
                    try:
                        normalized_doc = self.process_file(file, source_type)
                        normalized_dataset.append(normalized_doc)
                        print(f"✅ Cleaned [{source_type.upper()}]: {file.name}")
                    except Exception as e:
                        print(f"❌ Failed to parse {file.name}: {str(e)}")

        print(f"\n✨ Ingestion complete. Processed {len(normalized_dataset)} / 13 files.")
        return normalized_dataset

if __name__ == "__main__":
    # Point this to your local dummy directory path
    DUMMY_DATA_DIR = "./dummy_data" 
    
    ingestor = AuraIngestor(DUMMY_DATA_DIR)
    output_data = ingestor.run_pipeline()
    
    # Save the output to hand off to Tejus
    output_file = Path("normalized_ingestion_output.json")
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(output_data, out, indent=2, ensure_ascii=False)
        
    print(f"💾 Hand-off payload generated successfully at: '{output_file}'")