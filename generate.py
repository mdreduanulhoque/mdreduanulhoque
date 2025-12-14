import json
import datetime
import svgwrite

def get_color(hours):
    # Logic Re-check based on your prompt
    if hours == 0: 
        return "#D81159"      # 🔴 Red (0 hrs)
    if 0 < hours <= 2: 
        return "#FFBC42"      # 🟡 Gold (1-2 hrs)
    if 2 < hours < 5: 
        return "#D16014"      # 🟠 Orange (More than 2, less than 5)
    if hours >= 5: 
        return "#218380"      # 🟢 Green (5 or more)
    return "#ebedf0"          # ⚪ Grey (Empty/Future)

def generate_chart():
    # 1. Load Data
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # 2. Setup Canvas
    # 'profile' and 'xmlns' are crucial for visibility
    dwg = svgwrite.Drawing('progress.svg', profile='full', size=("850px", "160px"))
    dwg['xmlns'] = "http://www.w3.org/2000/svg"

    # 3. Calculate Stats (The "Toggle" View)
    total_hours = sum(data.values())
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    year_str = str(datetime.datetime.now().year)
    
    # Filter for current year only
    current_year_data = {k: v for k, v in data.items() if k.startswith(year_str)}
    year_hours = sum(current_year_data.values())

    # 4. Draw Header (Stats)
    dwg.add(dwg.text(f"🚀 YEARLY FOCUS: {year_hours} HRS | 🔥 TOTAL LIFETIME: {total_hours} HRS", 
                     insert=(10, 25), fill="#333", font_size="14px", font_family="monospace", font_weight="bold"))

    # 5. Draw the Grid
    box_size = 12
    gap = 4
    start_x = 0
    start_y = 40  # Moved down to make room for text
    
    year = datetime.datetime.now().year
    start_date = datetime.date(year, 1, 1)
    
    # Loop through 365/366 days
    current_day = start_date
    while current_day.year == year:
        # Calculate Grid Position (GitHub Style: Weeks go Right, Days go Down)
        week_num = int(current_day.strftime("%U"))
        day_of_week = int(current_day.strftime("%w")) # 0=Sunday
        
        x_pos = start_x + (week_num * (box_size + gap))
        y_pos = start_y + (day_of_week * (box_size + gap))
        
        # Get Hours & Color
        date_key = current_day.strftime("%Y-%m-%d")
        hours = data.get(date_key, -1) # Default -1 for no data
        
        # Logic for coloring
        if hours == -1:
            if current_day <= datetime.date.today():
                color = "#ebedf0" # Past day with no data (Grey)
            else:
                color = "#ebedf0" # Future day (Grey)
        else:
            color = get_color(hours)

        # Draw the box
        dwg.add(dwg.rect(insert=(x_pos, y_pos), size=(box_size, box_size), fill=color, rx=2))
        
        current_day += datetime.timedelta(days=1)

    dwg.save()
    print("✅ SVG Re-generated successfully.")

if __name__ == "__main__":
    generate_chart()
