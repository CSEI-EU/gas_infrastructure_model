import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# --- Project Info ---
start_date = datetime(2026, 9, 1)
project_months = 36

# --- Workpackages ---
workpackages = ["WP1", "WP2", "WP3", "WP4", "WP5", "WP6"]
wp_colors = px.colors.sequential.Blues  # unified shades of blue

# Define real WP timeframes (in months from project start)
# Format: (WP, start_month, end_month)
wp_timeline = [
    ("WP1", 1, 36),
    ("WP2", 1, 36),
    ("WP3", 1, 36),
    ("WP4", 13, 36),
    ("WP5", 1, 36),
    ("WP6", 1, 36)
]

# --- Partner Involvement Data ---
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
    start = start_date + timedelta(days=(start_month - 1) * 30)
    end = start_date + timedelta(days=end_month * 30)
    return start, end

# ---------------------------------------------------------------------
# --- Version 1: Workpackage-focused Gantt (custom times, not reversed)
# ---------------------------------------------------------------------

wp_chart_data = []
for wp, start_m, end_m in wp_timeline:
    start, end = months_to_dates(start_m, end_m)
    wp_chart_data.append({
        "Task": wp,
        "Start": start,
        "Finish": end
    })

wp_df = pd.DataFrame(wp_chart_data)
fig_wp = px.timeline(
    wp_df, x_start="Start", x_end="Finish", y="Task", color="Task",
    color_discrete_sequence=wp_colors
)
fig_wp.update_yaxes(autorange="normal")  # keep normal order
fig_wp.update_layout(
    title="Project Timeline",
    xaxis_title="Date",
    yaxis_title="Workpackage",
    plot_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="lightgrey"),
    yaxis=dict(showgrid=False)
)

# ---------------------------------------------------------------------
# --- Version 2: Partner-focused Gantt
# ---------------------------------------------------------------------

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
fig_partner = px.timeline(
    partner_df, x_start="Start", x_end="Finish", y="Partner",
    color="WP", color_discrete_sequence=wp_colors
)
fig_partner.update_yaxes(autorange="normal")
fig_partner.update_layout(
    title="Partner Involvement Timeline",
    xaxis_title="Date",
    yaxis_title="Partner",
    plot_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="lightgrey"),
    yaxis=dict(showgrid=False)
)

# ---------------------------------------------------------------------
# --- EVENTS: Meetings (lines), Milestones (◇), Deliverables (●)
# ---------------------------------------------------------------------

meetings = [
    {"Date": start_date + timedelta(days=15), "Name": "Kick-off meeting"},
    {"Date": start_date + timedelta(days=180), "Name": "Stakeholder Workshop I"},
    {"Date": start_date + timedelta(days=365), "Name": "Mid-term Meeting I"},
    {"Date": start_date + timedelta(days=540), "Name": "Stakeholder Workshop II"},
    {"Date": start_date + timedelta(days=730), "Name": "Mid-term Meeting II"},
    {"Date": start_date + timedelta(days=980), "Name": "Final Meeting"},
    {"Date": start_date + timedelta(days=1050), "Name": "Concluding Stakeholder Workshop"}
]

milestones = [
    {"Date": start_date + timedelta(days=30*8), "Name": "M1: Framework design completed", "WP": "WP1", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*16), "Name": "M2: Pilot assessment initiated", "WP": "WP2", "Partner": "DTU"},
    {"Date": start_date + timedelta(days=30*18), "Name": "M3: Cross-sector workshop 1 completed", "WP": "WP4", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*24), "Name": "M4: Commercial assessment validated", "WP": "WP3", "Partner": "CPH"},
    {"Date": start_date + timedelta(days=30*30), "Name": "M5: Investment roadmap finalized", "WP": "WP1", "Partner": "DTU"},
    {"Date": start_date + timedelta(days=30*36), "Name": "M6: Dissemination targets achieved", "WP": "WP6", "Partner": "CBS"}
]

# --- Deliverables from your table ---
deliverables = [
    {"Date": start_date + timedelta(days=30*8), "Name": "D1: Infrastructure capacity assessment report", "WP": "WP1", "Partner": "DTU"},
    {"Date": start_date + timedelta(days=30*8), "Name": "D2: Regulatory landscape mapping", "WP": "WP2", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*12), "Name": "D3: Technical compatibility framework", "WP": "WP1", "Partner": "DTU"},
    {"Date": start_date + timedelta(days=30*16), "Name": "D4: Policy scenario analysis", "WP": "WP2", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*12), "Name": "D5: Business model assessment", "WP": "WP3", "Partner": "CPH"},
    {"Date": start_date + timedelta(days=30*18), "Name": "D6: Risk-sharing framework", "WP": "WP3", "Partner": "POA"},
    {"Date": start_date + timedelta(days=30*12), "Name": "D7: First cross-portfolio workshop report", "WP": "WP4", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*6), "Name": "D8: Data governance protocols", "WP": "WP5", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*24), "Name": "D9: Infrastructure investment roadmap", "WP": "WP1", "Partner": "DTU"},
    {"Date": start_date + timedelta(days=30*30), "Name": "D10: Policy recommendation briefs", "WP": "WP2", "Partner": "CBS/DTU"},
    {"Date": start_date + timedelta(days=30*24), "Name": "D11: Demand aggregation framework", "WP": "WP3", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*30), "Name": "D12: Strategic learning synthesis report", "WP": "WP4", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*12), "Name": "D13: Project management reports", "WP": "WP5", "Partner": "CBS"},
    {"Date": start_date + timedelta(days=30*12), "Name": "D14: Scientific publication", "WP": "WP6", "Partner": "CBS/DTU"},
    {"Date": start_date + timedelta(days=30*24), "Name": "D14: Scientific publication", "WP": "WP6", "Partner": "CBS/DTU"},
    {"Date": start_date + timedelta(days=30*30), "Name": "D14: Scientific publication", "WP": "WP6", "Partner": "CBS/DTU"},
    {"Date": start_date + timedelta(days=30*36), "Name": "D15: Final sustainability report", "WP": "WP6", "Partner": "CBS"}
]

# font size etc.
fig_wp.update_yaxes(tickfont=dict(size=14, family="Arial"))
fig_partner.update_yaxes(tickfont=dict(size=14, family="Arial"))


# ---------------------------------------------------------------------
# --- Add Meetings (dashed lines) with titles ABOVE
# ---------------------------------------------------------------------
for fig, y_count in [(fig_wp, len(workpackages)), (fig_partner, len(partner_data))]:
    # Add dashed lines for all meetings
    for m in meetings:
        fig.add_shape(
            type="line",
            x0=m["Date"], x1=m["Date"],
            y0=-0.5, y1=y_count - 0.5,
            line=dict(color="rgba(0, 51, 160, 0.6)", width=2, dash="dot")
        )
        fig.add_annotation(
            x=m["Date"],
            y=y_count - 0.5,
            text=m["Name"],
            showarrow=False,
            yshift=25,
            font=dict(color="rgba(0, 51, 160, 0.9)", size=14, family="Arial"),
            align="center"
        )
    # Dummy Scatter for legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="lines",
        line=dict(color="rgba(0,51,160,0.9)", width=2, dash="dot"),
        name="Meeting/Workshop"
    ))

# ---------------------------------------------------------------------
# --- Add Milestones (diamond markers) and Deliverables (circle markers)
# ---------------------------------------------------------------------
for i, ms in enumerate(milestones):
    fig_wp.add_trace(go.Scatter(
        x=[ms["Date"]], y=[ms["WP"]],
        mode="markers+text",
        marker=dict(size=14, symbol="diamond", color="rgba(70,130,180,0.9)"),
        text=[ms["Name"]],
        textposition="top center",
        showlegend=(i == 0),
        name="Milestone",
        hoverinfo="text",
        textfont=dict(size=13)
    ))
    fig_partner.add_trace(go.Scatter(
        x=[ms["Date"]], y=[ms["Partner"]],
        mode="markers+text",
        marker=dict(size=14, symbol="diamond", color="rgba(70,130,180,0.9)"),
        text=[ms["Name"]],
        textposition="top center",
        showlegend=(i == 0),
        name="Milestone",
        hoverinfo="text",
        textfont=dict(size=13)
    ))

# Deliverables
for i, d in enumerate(deliverables):
    fig_wp.add_trace(go.Scatter(
        x=[d["Date"]], y=[d["WP"]],
        mode="markers+text",
        marker=dict(size=12, symbol="circle", color="rgba(0,51,160,0.9)"),
        text=[d["Name"]],
        textposition="bottom center",
        showlegend=(i == 0),
        name="Deliverable",
        hoverinfo="text",
        textfont=dict(size=13)
    ))
    fig_partner.add_trace(go.Scatter(
        x=[d["Date"]], y=[d["Partner"]],
        mode="markers+text",
        marker=dict(size=12, symbol="circle", color="rgba(0,51,160,0.9)"),
        text=[d["Name"]],
        textposition="bottom center",
        showlegend=(i == 0),
        name="Deliverable",
        hoverinfo="text",
        textfont=dict(size=13)
    ))

# --- Update layout legend ---
fig_wp.update_layout(legend=dict(font=dict(size=12)))
fig_partner.update_layout(legend=dict(font=dict(size=12)))

# --- Show figures ---
fig_wp.show()
fig_partner.show()


