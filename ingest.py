import os
import json
import re
from datetime import datetime
from pathlib import Path
from email import message_from_string

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
            "title": title,
            "author": author,
            "date": date_str
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
            # Simple manual fallback parsing
            lines = content.split('\n')
            for line in lines[:10]: # Look at top lines
                if line.startswith('From:'): author = line.replace('From:', '').strip()
                elif line.startswith('Subject:'): title = line.replace('Subject:', '').strip()
                elif line.startswith('Date:'): date_raw = line.replace('Date:', '').strip()
        
        # Clean up fallback body if standard parsing returned empty
        body = msg.get_payload() if msg.is_multipart() is False else content
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
            "title": file_path.stem.replace('_', ' ').replace('-', ' ').title(),
            "author": None,
            "date": None
        }

    def process_file(self, file_path: Path, source_type: str) -> dict:
        """Transforms raw files into the common AURA-KG ingestion contract."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        metadata = {"title": None, "author": None, "date": None}
        raw_text = content

        if source_type == 'note':
            metadata = self.parse_note(content, file_path)
            # Re-read or isolate text if using frontmatter
            if frontmatter and content.startswith('---'):
                raw_text = frontmatter.loads(content).content
            elif content.startswith('---') and len(content.split('---', 2)) >= 3:
                raw_text = content.split('---', 2)[2]
                
        elif source_type == 'email':
            email_data = self.parse_email(content)
            metadata = email_data["metadata"]
            raw_text = email_data["body"]
            
        elif source_type == 'document':
            metadata = self.parse_document(content, file_path)

        return {
            "source_type": source_type,
            "source_path": str(file_path.relative_to(self.data_dir.parent)),
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