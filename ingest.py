from pathlib import Path
from app.services.chunking import chunker, MarkdownChunker
from app.db.vector_store import vector_store
from typing import List
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_data():
    """
    Reads all markdown files from data/ directory, chunks them,
    and uploads them to Pinecone.
    """
    # 1. Define data directory
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    
    if not data_dir.exists():
        logger.error(f"Data directory not found at {data_dir}")
        return

    # 2. Wait for Index Readiness
    try:
        logging.info(f"Checking access to Pinecone index '{vector_store.index_name}'...")
        stats = vector_store.index.describe_index_stats()
        logging.info(f"Index accessible. Current stats: {stats}")
    except Exception as e:
        logger.error(f"Failed to access Pinecone index: {e}")
        return

    # 3. Iterate over all markdown files
    md_files = list(data_dir.glob("*.md"))
    if not md_files:
        logger.warning("No markdown files found in data directory.")
        return

    total_chunks = 0
    
    for file_path in md_files:
        logger.info(f"Processing {file_path.name}...")
        
        # 4. Chunk the file
        file_chunks = chunker.process_file(file_path)
        
        if not file_chunks:
            logger.warning(f"No chunks created for {file_path.name}")
            continue
            
        logger.info(f"Generated {len(file_chunks)} chunks for {file_path.name}")
        
        # 5. Upload to Pinecone
        try:
            vector_store.upsert_chunks(file_chunks)
            total_chunks += len(file_chunks)
            logger.info(f"Successfully uploaded chunks for {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to upload chunks for {file_path.name}: {e}")

    logger.info("Ingestion complete!")
    logger.info(f"Total files processed: {len(md_files)}")
    logger.info(f"Total chunks uploaded: {total_chunks}")

if __name__ == "__main__":
    ingest_data()
