import re
import json

def extract(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"--- Extracted from {filename} ---")
    
    # Try to find description in meta tags
    meta_desc = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', content)
    if meta_desc:
        print("Meta Description:", meta_desc.group(1))
        
    title = re.search(r'<title>([^<]+)</title>', content)
    if title:
        print("Title:", title.group(1))
        
    # Look for SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__ which contain the video metadata
    sigi = re.search(r'window\[\'SIGI_STATE\'\]=(.*?);window', content)
    if sigi:
        try:
            data = json.loads(sigi.group(1))
            items = data.get('ItemModule', {})
            for k, v in items.items():
                print("Video Desc:", v.get('desc', ''))
        except:
            pass
            
    univ = re.search(r'__UNIVERSAL_DATA_FOR_REHYDRATION__=(.*?)</script>', content)
    if univ:
        try:
            data = json.loads(univ.group(1))
            # Just print the whole thing roughly to grep
            s = json.dumps(data, ensure_ascii=False)
            match = re.search(r'"desc":"([^"]+)"', s)
            if match:
                print("Video Desc (univ):", match.group(1))
        except:
            pass

extract(r'C:\Users\dathao\.gemini\antigravity-ide\brain\819f9274-5fa4-44ee-ba7f-54bc81660517\.system_generated\steps\562\content.md')
extract(r'C:\Users\dathao\.gemini\antigravity-ide\brain\819f9274-5fa4-44ee-ba7f-54bc81660517\.system_generated\steps\563\content.md')
