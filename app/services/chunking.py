import re
from typing import List, Dict, Optional
from pathlib import Path
import logging

class MarkdownChunker:
    """
    Advanced Markdown Chunker specific for RAG portfolios.
    Implements Strategy B: Split by Both Primary (##) and Secondary (###) Headers.
    """
    def __init__(self):
        # Matches ## Header (Primary)
        self.h2_pattern = re.compile(r'^(##)\s+(.+)$', re.MULTILINE)
        # Matches ### Header (Secondary)
        self.h3_pattern = re.compile(r'^(###)\s+(.+)$', re.MULTILINE)

    def _clean_content(self, text: str) -> str:
        """Removes extra newlines and whitespace."""
        return text.strip()
        
    def _word_count(self, text: str) -> int:
        return len(text.split())

    def _get_section_type(self, filename: str) -> str:
        """Maps filename to logic section type."""
        name = filename.lower()
        if "project" in name: return "project"
        if "experience" in name or "work" in name: return "experience"
        if "skill" in name: return "skill"
        if "education" in name: return "education"
        if "personal" in name: return "personal"
        return "general"

    def process_file(self, file_path: Path) -> List[Dict]:
        """
        Reads a markdown file and splits it into semantic chunks based on headers.
        Returns a list of dicts with 'id', 'text', and 'metadata'.
        """
        content = file_path.read_text(encoding='utf-8')
        filename = file_path.name
        section_type = self._get_section_type(filename)
        
        chunks = []
        
        # 1. Split by H2 first
        h2_splits = re.split(r'(^##\s+.+$)', content, flags=re.MULTILINE)
        
        # Handle intro content
        if h2_splits[0].strip():
            intro_text = h2_splits[0].strip()
            if self._word_count(intro_text) > 5:
                chunks.append({
                    "id": f"{filename}-intro",
                    "text": intro_text,
                    "metadata": {
                        "source": filename,
                        "header": "Introduction",
                        "header_level": "H1",
                        "section_type": section_type,
                        "word_count": self._word_count(intro_text)
                    }
                })
            
        current_h2_title = "Global"
        
        # Safely iterate through splits in pairs [Header, Body]
        # Use length-1 to safely access i+1
        for i in range(1, len(h2_splits) - 1, 2):
            h2_header_line = h2_splits[i].strip()
            # Double check bounds just in case
            if i + 1 >= len(h2_splits):
                break
                
            h2_body = h2_splits[i+1]
            current_h2_title = h2_header_line.replace("##", "").strip()
            
            # NOW Check for H3s within this H2 block
            h3_splits = re.split(r'(^###\s+.+$)', h2_body, flags=re.MULTILINE)
            
            if len(h3_splits) == 1:
                # Strategy A: No subsections
                final_text = f"{h2_header_line}\n{h2_body.strip()}"
                if self._word_count(final_text) > 5:
                    chunks.append({
                        "id": f"{filename}-{len(chunks)}",
                        "text": final_text,
                        "metadata": {
                            "source": filename,
                            "header": current_h2_title,
                            "header_level": "H2",
                            "section_type": section_type,
                            "word_count": self._word_count(final_text)
                        }
                    })
            else:
                # Strategy B: We have subsections
                
                # Check for "Intro" content under H2
                if h3_splits[0].strip():
                    intro_text = f"{h2_header_line}\n{h3_splits[0].strip()}"
                    if self._word_count(intro_text) > 5:
                        chunks.append({
                            "id": f"{filename}-{len(chunks)}",
                            "text": intro_text,
                            "metadata": {
                                "source": filename,
                                "header": current_h2_title,
                                "header_level": "H2",
                                "section_type": section_type,
                                "word_count": self._word_count(intro_text)
                            }
                        })
                
                # Process H3 chunks safely
                for j in range(1, len(h3_splits) - 1, 2):
                    if j + 1 >= len(h3_splits):
                        break
                        
                    h3_header_line = h3_splits[j].strip()
                    h3_body = h3_splits[j+1].strip()
                    h3_title = h3_header_line.replace("###", "").strip()
                    
                    final_text = f"{h2_header_line}\n{h3_header_line}\n{h3_body}"
                    
                    if self._word_count(final_text) > 5:
                        chunks.append({
                            "id": f"{filename}-{len(chunks)}",
                            "text": final_text,
                            "metadata": {
                                "source": filename,
                                "header": f"{current_h2_title} > {h3_title}",
                                "header_level": "H3",
                                "section_type": section_type,
                                "word_count": self._word_count(final_text)
                            }
                        })

        return chunks

chunker = MarkdownChunker()
