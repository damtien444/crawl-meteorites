# Required Libraries
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# Target URL
url = 'https://www.imo.net/resources/calendar/'

# Send request and parse the page
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find event sections - using the correct structure from the page
events = []

# The meteor shower data is in div elements with class 'media-body'
shower_divs = soup.find_all('div', class_='media-body')

if not shower_divs:
    print("No meteor shower data found. The page structure might have changed.")
else:
    for shower_div in shower_divs:
        event_data = {
            'name': '',
            'code': '',
            'description': '',
            'peak': '',
            'active_period': '',
            'zhr': '',
            'velocity_km_s': '',
            'radiant': '',
            'parent_body': ''
        }
        
        # Get the meteor shower name from h3 inside the media-body div
        name_element = shower_div.find('h3', class_='media-heading')
        if name_element:
            full_name = name_element.get_text(strip=True)
            # Extract code from parentheses if present
            code_match = re.search(r'\(([A-Z]+)\)', full_name)
            if code_match:
                event_data['code'] = code_match.group(1)
                event_data['name'] = full_name.split('(')[0].strip()
            else:
                event_data['name'] = full_name
        
        # Get the active period from span with class 'shower_acti'
        period_span = shower_div.find('span', class_='shower_acti')
        if period_span:
            event_data['active_period'] = period_span.get_text(strip=True)
        
        # Description is in paragraphs within the div
        description_paragraphs = shower_div.find_all('p')
        if description_paragraphs:
            description_text = ''
            for p in description_paragraphs:
                # Skip paragraphs that contain "Shower details"
                if p.find('strong') and "Shower details" in p.find('strong').get_text(strip=True):
                    continue
                description_text += p.get_text(strip=True) + ' '
            
            # Clean up the description
            event_data['description'] = description_text.strip()
            
            # Try to extract peak, ZHR, velocity, radiant, and parent body from the description
            if 'peak' in event_data['description'].lower() or 'maximum' in event_data['description'].lower():
                peak_match = re.search(r'peak\s+near\s+([^\.]+)', event_data['description'], re.IGNORECASE)
                if peak_match:
                    event_data['peak'] = peak_match.group(1).strip()
            
            if 'hourly rates' in event_data['description'].lower() or 'zhr' in event_data['description'].lower():
                zhr_match = re.search(r'hourly\s+rates[^\d]*(\d+(?:-\d+)?)', event_data['description'], re.IGNORECASE)
                if zhr_match:
                    event_data['zhr'] = zhr_match.group(1).strip()
            
            if 'km/s' in event_data['description'].lower() or 'velocity' in event_data['description'].lower():
                velocity_match = re.search(r'velocity\s+[^\d]*(\d+(?:\.\d+)?)\s*km/s', event_data['description'], re.IGNORECASE)
                if velocity_match:
                    event_data['velocity_km_s'] = velocity_match.group(1).strip()
            
            if 'radiant' in event_data['description'].lower():
                radiant_match = re.search(r'radiant\s+(?:is\s+)?(?:located\s+)?([^\.]+)', event_data['description'], re.IGNORECASE)
                if radiant_match:
                    event_data['radiant'] = radiant_match.group(1).strip()
            
            if 'comet' in event_data['description'].lower() or 'asteroid' in event_data['description'].lower():
                parent_match = re.search(r'(?:comet|asteroid)\s+([^\s\.]+)', event_data['description'], re.IGNORECASE)
                if parent_match:
                    event_data['parent_body'] = parent_match.group(1).strip()
        
        # Only add events that have a name (to filter out any empty divs)
        if event_data['name']:
            events.append(event_data)

# Save as JSON
with open('meteor_showers_imo.json', 'w', encoding='utf-8') as f:
    json.dump({"meteor_showers": events}, f, ensure_ascii=False, indent=2)

print(f"Scraping completed. Found {len(events)} meteor showers. Data saved to 'meteor_showers_imo.json'")
