import asyncio

from pathlib import Path

from database import dataDir
from tgf_parser import chapterDir

def _merge_files_sync(head: int, tail: int):
    mergeDir = dataDir / 'merge_files'
    if not mergeDir.exists():
        mergeDir.mkdir(parents=True, exist_ok=True)

    if head > tail: 
        head, tail = tail, head
    fileName = f"merged_{head}-{tail}.txt" 
    
    out_path = mergeDir / fileName

    with out_path.open(mode="w", encoding="utf-8") as out_file:
        for i in range(head, tail + 1):
            in_path = chapterDir / f"{i}" / f"{i}.txt"
            
            with in_path.open( encoding="utf-8") as in_file:
                for line in in_file:
                    out_file.write(line)
            out_file.write('\n')
    
    return out_path
        
async def merge_files(head: int, tail:int):
    return await asyncio.to_thread(_merge_files_sync, head, tail)