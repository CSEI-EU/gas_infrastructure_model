import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# --- Project Info ---
start_date = datetime(2025, 9, 26)
project_months = 36

# --- Workpackages ---
workpackages = ["WP1", "WP2", "WP3", "WP4", "WP5", "WP6"]
wp_colors = px.colors.qualitative.Plotly  # 6 colors

# --- Partner Involvement Data ---
# Format: Partner: [(WP, start_month, end_month), ...]
partner_data = {
    "CBS": [(1, 3, 16), (2, 20, 26)],
    "DTU": [(1, 1, 12), (3, 15, 24)],
    "CE": [(2, 5, 18)],
    "MMKMC": [(4, 10, 22)],
    "CPH": [(3, 2, 20)],
    "AAP": [(5, 12, 30)],
    "Carrier": [(6, 1, 36)],
    "Airline": [(2, 8, 18), (4, 20, 28)]
}

# --- Helper function to convert months to dates ---
def months_to_dates(start_month, end_month):
    start = start_date + timedelta(days=(start_month-1)*30)
    end = start_date + timedelta(days=end_month*30)
    return start, end

# --- Version 1: Workpackage-focused Gantt ---
wp_chart_data = []
for wp in workpackages:
    # Example: you can customize WP periods here
    wp_chart_data.append({
        "Task": wp,
        "Start": start_date + timedelta(days=(workpackages.index(wp)*6*30)),  # dummy start
        "Finish": start_date + timedelta(days=((workpackages.index(wp)+1)*6*30))
    })

wp_df = pd.DataFrame(wp_chart_data)
fig_wp = px.timeline(wp_df, x_start="Start", x_end="Finish", y="Task", color="Task",
                     color_discrete_sequence=wp_colors)
fig_wp.update_yaxes(autorange="reversed")
fig_wp.update_layout(title="Project Workpackages Timeline")

# --- Version 2: Partner-focused Gantt ---
partner_chart_data = []
for partner, periods in partner_data.items():
    for wp, start_m, end_m in periods:
        start, end = months_to_dates(start_m, end_m)
        partner_chart_data.append({
            "Partner": partner,
            "Start": start,
            "Finish": end,
            "WP": f"WP{wp}"
        })

partner_df = pd.DataFrame(partner_chart_data)
fig_partner = px.timeline(partner_df, x_start="Start", x_end="Finish", y="Partner",
                          color="WP", color_discrete_sequence=wp_colors)
fig_partner.update_yaxes(autorange="reversed")
fig_partner.update_layout(title="Partner Involvement Timeline")

# --- Optional: Add Milestones and Workshops ---
milestones = [
    {"Date": start_date + timedelta(days=180), "Name": "Kick-off Workshop"},
    {"Date": start_date + timedelta(days=365), "Name": "Mid-term Milestone"},
    {"Date": start_date + timedelta(days=730), "Name": "Final Milestone"}
]

for milestone in milestones:
    fig_wp.add_shape(
        dict(
            type="line",
            x0=milestone["Date"], x1=milestone["Date"],
            y0=-0.5, y1=len(workpackages)-0.5,
            line=dict(color="red", width=2, dash="dot")
        )
    )
    fig_wp.add_annotation(
        dict(
            x=milestone["Date"], y=-0.5,
            text=milestone["Name"],
            showarrow=True, arrowhead=1
        )
    )
    fig_partner.add_shape(
        dict(
            type="line",
            x0=milestone["Date"], x1=milestone["Date"],
            y0=-0.5, y1=len(partner_data)-0.5,
            line=dict(color="red", width=2, dash="dot")
        )
    )
    fig_partner.add_annotation(
        dict(
            x=milestone["Date"], y=-0.5,
            text=milestone["Name"],
            showarrow=True, arrowhead=1
        )
    )

# --- Show figures ---
fig_wp.show()
fig_partner.show()
