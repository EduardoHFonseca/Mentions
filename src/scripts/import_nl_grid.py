import os
import sys
import re
from datetime import datetime, time, date, timedelta
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.database import SQLALCHEMY_DATABASE_URL
from src.models.models import ProgrammingGrid

def fetch_and_import_nl_grid():
    print("Fetching TVGids.nl guide page...")
    url = "https://www.tvgids.nl/gids/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print(f"Error fetching TVGids.nl: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    
    # 1. Extract channel names from navigation
    nav = soup.find("div", class_="guide__channel-navigation")
    if not nav:
        print("Error: guide__channel-navigation not found")
        return
    
    channels = [a.text.strip() for a in nav.find_all("a")]
    print(f"Detected Dutch channels from nav: {channels}")
    if not channels:
        print("Error: No channels found in navigation")
        return

    # 2. Extract programs grouped by channel index
    # We will store: channel_idx -> list of programs (start_time_str, title, description, is_live, tags, img_url)
    channel_programs = {i: [] for i in range(len(channels))}
    
    gc = soup.find("div", class_="guide__guide-container")
    if not gc:
        print("Error: guide__guide-container not found")
        return
    
    rows = gc.find_all("div", class_=lambda c: c and "guide__hour-row" in c)
    print(f"Found {len(rows)} hour rows to process...")
    
    for row in rows:
        cols = row.find_all("div", class_="guide__hour-col")
        for col_idx, col in enumerate(cols):
            if col_idx >= len(channels):
                continue
                
            prog_a = col.find("a", class_="program__info")
            if not prog_a:
                continue
                
            # Extract start time (format: HH:MM)
            starttime_div = prog_a.find(class_="program__starttime")
            if not starttime_div:
                continue
                
            time_match = re.search(r"(\d{2}):(\d{2})", starttime_div.text)
            if not time_match:
                continue
            time_str = time_match.group(0)
            
            # Extract title
            title_el = prog_a.find(class_="program__title")
            title = title_el.text.strip() if title_el else "Unknown Program"
            
            # Extract description
            desc_el = prog_a.find(class_="program__text")
            desc = desc_el.text.strip() if desc_el else ""
            
            # Extract labels (tags)
            labels_div = prog_a.find(class_="program__labels")
            tags = []
            is_live = False
            if labels_div:
                for span in labels_div.find_all("span"):
                    lbl_text = span.text.strip()
                    # Map to friendly tags
                    if lbl_text == "h":
                        tags.append("REPRISE")
                    elif lbl_text == "L":
                        tags.append("LIVE")
                        is_live = True
                    elif lbl_text == "S":
                        tags.append("SPORT")
                    elif lbl_text == "A":
                        tags.append("NEWS")
                    elif lbl_text == "Tip":
                        tags.append("TIP")
                    else:
                        if lbl_text:
                            tags.append(lbl_text.upper())
            
            # Extract thumbnail image
            img_el = prog_a.find("img", class_="program__thumbnail")
            img_url = ""
            if img_el:
                img_url = img_el.get("data-src") or img_el.get("src") or ""
            
            # Store structured data
            # De-duplicate: don't add the same program with same start time consecutively
            existing_progs = channel_programs[col_idx]
            if not existing_progs or existing_progs[-1][0] != time_str or existing_progs[-1][1] != title:
                channel_programs[col_idx].append((time_str, title, desc, is_live, tags, img_url))

    # 3. Connect to Database
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 4. Clear existing NL grid
    print("Clearing existing NL programming grid...")
    session.query(ProgrammingGrid).filter(ProgrammingGrid.market == "NL").delete()
    session.commit()
    
    # 5. Populate grid for Monday June 22, 2026 to Sunday June 28, 2026 (7 days)
    start_date = date(2026, 6, 22)
    records_to_add = []
    
    for day_offset in range(7):
        target_date = start_date + timedelta(days=day_offset)
        
        for col_idx, channel_name in enumerate(channels):
            progs = channel_programs[col_idx]
            if not progs:
                continue
                
            # Sort programs by start time
            progs_sorted = sorted(progs, key=lambda x: x[0])
            
            for idx, (time_str, title, desc, is_live, tags, img_url) in enumerate(progs_sorted):
                h, m = map(int, time_str.split(":"))
                s_time = time(h, m)
                
                # Compute end_time based on next program
                e_time = None
                if idx + 1 < len(progs_sorted):
                    next_time_str = progs_sorted[idx+1][0]
                    next_h, next_m = map(int, next_time_str.split(":"))
                    # If next time is before start time, it means it crosses midnight
                    if next_h < h or (next_h == h and next_m < m):
                        e_time = time(23, 59)
                    else:
                        e_time = time(next_h, next_m)
                else:
                    # Last program of the day: default to 1 hour after or midnight
                    full_dt = datetime.combine(datetime.today(), s_time) + timedelta(hours=1)
                    e_time = full_dt.time()
                
                # Format metadata into the description column
                meta_parts = []
                if tags:
                    meta_parts.append(f"|TAGS: {','.join(tags)}|")
                if img_url:
                    meta_parts.append(f"|IMG: {img_url}|")
                
                final_desc = " ".join(meta_parts)
                if final_desc and desc:
                    final_desc += " " + desc
                elif not final_desc:
                    final_desc = desc
                
                grid_entry = ProgrammingGrid(
                    channel=channel_name.upper().strip(),
                    broadcast_date=target_date,
                    start_time=s_time,
                    end_time=e_time,
                    program_name=title,
                    description=final_desc,
                    market="NL",
                    is_live=is_live
                )
                records_to_add.append(grid_entry)
                
    if records_to_add:
        session.bulk_save_objects(records_to_add)
        session.commit()
        print(f"✓ Successfully imported {len(records_to_add)} programs with enriched metadata for Netherlands (NL) market!")
    else:
        print("! No valid programs parsed to import.")
        
    session.close()

if __name__ == "__main__":
    fetch_and_import_nl_grid()
