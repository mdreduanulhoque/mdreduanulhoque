import json
import datetime
import svgwrite # You need to put 'svgwrite' in requirements.txt

# 🎨 Color Configuration (NO BLUE)
def get_color(hours):
    if hours == 0: return "#FF0000"       # 🔴 Red
    if 0 < hours <= 2: return "#FFD700"   # 🟡 Gold (1-2 hrs)
    if 2 < hours <= 5: return "#FFA500"   # 🟠 Orange (2-4 hrs)
    if hours > 5: return "#006400"        # 🟢 Dark Green (5+ hrs)
    return "#ebedf0"                      # ⚪ Grey (Future/Empty)

def generate_chart():
    # 1. Load Data
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # 2. Setup Dimensions
    year = datetime.datetime.now().year
    start_date = datetime.date(year, 1, 1)
    
    # SVG Setup
    dwg = svgwrite.Drawing('progress.svg', profile='tiny', size=("800px", "200px"))
    
    # 3. Stats Calculation 🧮
    total_hours = sum(data.values())
    today = datetime.date.today().strftime("%Y-%m-%d")
    current_month = datetime.date.today().strftime("%Y-%m")
    
    month_hours = sum(h for d, h in data.items() if d.startswith(current_month))
    
    # Add Stats Text (Visual "Toggle" Replacement)
    dwg.add(dwg.text(f"🔥 TOTAL: {total_hours} hrs | 📅 THIS MONTH: {month_hours} hrs", 
                     insert=(10, 20), fill="black", font_size="14px", font_family="Arial"))

    # 4. Draw the Grid (GitHub Style)
    box_size = 12
    gap = 3
    start_x = 0
    start_y = 30
    
    # Loop through all days of the year
    current_day = start_date
    while current_day.year == year:
        # Calculate Position
        week_num = int(current_day.strftime("%U"))
        day_of_week = int(current_day.strftime("%w")) # 0=Sunday, 6=Saturday
        
        x_pos = start_x + (week_num * (box_size + gap))
        y_pos = start_y + (day_of_week * (box_size + gap))
        
        # Get Hours and Color
        date_str = current_day.strftime("%Y-%m-%d")
        hours = data.get(date_str, -1) # -1 indicates no data entered yet
        
        if hours == -1 and current_day > datetime.date.today():
             color = "#ebedf0" # Future
        elif hours == -1:
             color = "#ebedf0" # Past but no entry (treat as empty or 0 based on preference)
        else:
             color = get_color(hours)

        # Draw Box
        dwg.add(dwg.rect(insert=(x_pos, y_pos), size=(box_size, box_size), fill=color, rx=2))
        
        current_day += datetime.timedelta(days=1)

    dwg.save()
    print("✅ SVG Generated!")

if __name__ == "__main__":
    generate_chart()
