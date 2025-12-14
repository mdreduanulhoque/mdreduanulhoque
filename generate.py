import pandas as pd
import requests
import datetime
import svgwrite
from io import StringIO

# 🌐 PASTE YOUR GOOGLE SHEETS CSV EXPORT LINK HERE:
# Example: https://docs.google.com/spreadsheets/d/1xtyb2hBfNScEewEQXG__3sGENkSY6WqdEWieGk2baiA/export?format=csv&gid=0
GOOGLE_SHEET_CSV_URL = "YOUR_GOOGLE_SHEET_CSV_EXPORT_URL_HERE" 

# --- Color Configuration ---
def get_color(hours):
    # Colors based on your request (No Blue)
    if hours == 0: 
        return "#D81159"      # 🔴 Red (0 hrs)
    if 0 < hours <= 2: 
        return "#FFBC42"      # 🟡 Gold (1-2 hrs)
    if 2 < hours < 5: 
        return "#D16014"      # 🟠 Orange (3-4 hrs)
    if hours >= 5: 
        return "#218380"      # 🟢 Green (5+ hrs)
    return "#ebedf0"          # ⚪ Grey (Empty/Future)

# --- Data Fetching ---
def fetch_and_process_data():
    try:
        response = requests.get(GOOGLE_SHEET_CSV_URL)
        response.raise_for_status() 

        data_io = StringIO(response.text)
        # Read CSV. Assumes first column is Date and second is Hours.
        df = pd.read_csv(data_io)
        
        # Ensure column names are set correctly based on the CSV headers
        df.columns = ['Date', 'Hours'] 
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        # Returns {"YYYY-MM-DD": hours}
        return {str(k): int(v) for k, v in df.set_index('Date')['Hours'].to_dict()}

    except Exception as e:
        print(f"❌ Error fetching or processing data from Google Sheet: {e}")
        # Return empty data so the script doesn't crash, it just draws an empty grid.
        return {}


# --- SVG Drawing ---
def generate_chart():
    data = fetch_and_process_data()

    # Dimensions
    box_size = 12
    gap = 4
    start_x = 10 
    start_y_grid = 45 # Space for the legend above

    # SVG Setup
    # 
    dwg = svgwrite.Drawing('progress.svg', profile='full', size=("850px", "160px"))
    dwg['xmlns'] = "http://www.w3.org/2000/svg"

    # 1. Draw Color Legend 🎨
    legend_y = 25
    
    dwg.add(dwg.text("Color Legend:", insert=(start_x, legend_y), fill="#333", font_size="12px", font_weight="bold"))
    
    legend_items = [
        (0, "#D81159", "0 hrs"),
        (1, "#FFBC42", "1-2 hrs"),
        (3, "#D16014", "3-4 hrs"),
        (5, "#218380", "5+ hrs"),
        (-1, "#ebedf0", "No Data/Future")
    ]
    
    current_x = 110 # Starting point for the first color box
    
    for hours, color, label in legend_items:
        dwg.add(dwg.rect(insert=(current_x, legend_y-10), size=(box_size, box_size), fill=color, rx=2))
        dwg.add(dwg.text(label, insert=(current_x + box_size + 5, legend_y), fill="#333", font_size="10px"))
        current_x += 100 

    # 2. Draw the Grid and Month Dividers
    year = datetime.datetime.now().year
    start_date = datetime.date(year, 1, 1)
    
    current_day = start_date
    last_month = 0
    
    while current_day.year == year:
        date_key = current_day.strftime("%Y-%m-%d")
        
        week_num = int(current_day.strftime("%U"))
        day_of_week = int(current_day.strftime("%w")) # 0=Sunday
        
        x_pos = start_x + (week_num * (box_size + gap))
        y_pos = start_y_grid + (day_of_week * (box_size + gap))
        
        hours = data.get(date_key, -1) 
        color = get_color(hours)

        # Draw the box
        dwg.add(dwg.rect(insert=(x_pos, y_pos), size=(box_size, box_size), fill=color, rx=2))
        
        # Month Divider Logic
        if current_day.month != last_month and current_day.day <= 7:
             # Draw the month abbreviation label
            month_abbr = current_day.strftime("%b") # e.g., "Jan", "Feb"
            dwg.add(dwg.text(month_abbr, insert=(x_pos, start_y_grid - 10), 
                             fill="#666", font_size="10px"))

            # Draw a vertical line for the month boundary
            dwg.add(dwg.line(start=(x_pos - (gap/2)), end=(x_pos - (gap/2)), 
                             start_y=start_y_grid - 2, 
                             end_y=start_y_grid + (7 * (box_size + gap)) - gap + 2, 
                             stroke="#999999", stroke_width=0.5))
                             
        last_month = current_day.month
        current_day += datetime.timedelta(days=1)

    dwg.save()
    print("✅ SVG Re-generated successfully with Legend and Month Lines.")

if __name__ == "__main__":
    generate_chart()
