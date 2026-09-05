import pandas as pd
import plotly.graph_objects as go
import gradio as gr


df = pd.read_csv("ZoonoIntel - Final App Data.csv")


driver_name_map = {
    "geographic_range_area_km2": "Geographic Range (Km²)",
    "human_population_density": "Human Population Density",
    "climate_change_exposure": "Climate Change Exposure",
    "habitat_loss_rate": "Habitat Loss Rate",
    "trade_volume": "Wildlife Trade Volume",
    "host_plasticity": "Host Plasticity",
    "viral_sharing_score": "Viral Sharing Score",
    "phylogenetic_risk": "Phylogenetic Risk",
    "urbanization_overlap": "Urbanization Overlap",
    "temperature_variability": "Temperature Variability",
    "precipitation_variability": "Precipitation Variability",
    "adult_body_mass_g": "Adult Body Mass (g)",
    "precipitation_mean_mm": "Precipitation Mean (mm)"
}

def create_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            "suffix": " / 100",
            "font": {"color": "white", "size": 36}
        },
        title={
            "text": "<b>ZoonoIntel Sentinel Score</b>",
            "font": {"color": "#00AEEF", "size": 24}  # Blue title
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "white",
                "tickfont": {"color": "white", "size": 14}
            },

            # Needle bar → BLUE
            "bar": {"color": "#0070D4"},

            # Background of gauge
            "bgcolor": "#0A1A2F",

            # Updated brand-colored segments
            "steps": [
                {"range": [0, 25], "color": "rgba(0,200,83,0.6)"},   # Green (new low)
                {"range": [25, 50], "color": "rgba(255,215,0,0.6)"}, # Yellow (new mid)
                {"range": [50, 75], "color": "rgba(255,122,0,0.6)"}, # Orange (unchanged)
                {"range": [75, 100], "color": "rgba(230,57,70,0.7)"},# Red (unchanged)
            ],

            # Blue border for polish
            "bordercolor": "#00AEEF",
            "borderwidth": 2,
        }
    ))

    fig.update_layout(
        height=340,
        margin=dict(l=30, r=30, t=70, b=30),
        paper_bgcolor="#0A1A2F",
        font={"color": "white"}
    )

    return fig

    # Find ALL partial matches
    matches = df[
        df["species_name"].str.lower().str.contains(q, na=False)
        | df["common_Name"].str.lower().str.contains(q, na=False)
    ]

    if matches.empty:
        return gr.update(choices=[], value=None, visible=False), "", None, gr.update(visible=False), "No species found."

    # Build dropdown list: "Common Name (Scientific Name)"
    options = [
        f"{row['common_Name']} ({row['species_name']})"
        for _, row in matches.iterrows()
    ]

    return gr.update(choices=options, value=None, visible=True), "", None, gr.update(visible=False), "Select a species."

species_dropdown = gr.Dropdown(
    label="Matching species",
    choices=[],
    visible=False
)
    
def load_species(selection):
    if not selection:
        return "", None, gr.update(visible=False), ""

    # Extract scientific name from "Common Name (Scientific Name)"
    sci_name = selection.split("(")[-1].replace(")", "").strip()

    row = df[df["species_name"] == sci_name].iloc[0]

    score = row["zoonointel_score"]
    gauge = create_gauge(score)

    name_md = f"## {row['common_Name']} ({row['species_name']})"

    d1 = driver_name_map.get(row.get("top_driver_1", ""), row.get("top_driver_1", ""))
    d2 = driver_name_map.get(row.get("top_driver_2", ""), row.get("top_driver_2", ""))
    d3 = driver_name_map.get(row.get("top_driver_3", ""), row.get("top_driver_3", ""))

    report = f"""
## **Taxonomy**
**Order:** {row['order']}<br>
**Family:** {row['family']}

----

## **ZoonoIntel Resevoir Potential Prediction**
**Sentinel Score:** {score} / 100 <br>
**Sentinel Tier:** {row['risk_tier']}

----

## **Top Positive Drivers**
1. {d1}
2. {d2}
3. {d3}

----

## **Uncertainty Notes**
{row.get('uncertainty_reason', 'None')}
"""

    return name_md, gauge, gr.update(visible=True), report

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@300;400;500;700&display=swap');

:root {
    color-scheme: dark !important;
    --primary-color: #00AEEF;
    --secondary-color: #FF7A00;
    --accent-color: #00C853;
    --text-color: #FFFFFF;
    --font-family: 'Orbitron', sans-serif;
}

/* Global font */
* {
    font-family: var(--font-family) !important;
}

/* MATCH WEBSITE BACKGROUND */
.gradio-container {
    background: linear-gradient(120deg, #00111f, #002b45, #003b5c, #001f33) !important;
    background-size: 400% 400% !important;
    animation: nebulaShift 18s ease infinite !important;
    color: var(--text-color) !important;
    position: relative;
    overflow: hidden;
}

/* Animated background shift */
@keyframes nebulaShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* PARTICLE LAYER */
.particles {
    position: fixed;
    inset: 0;
    z-index: -2;
    overflow: hidden;
    pointer-events: none;
}

.particle {
    position: absolute;
    width: 3px;
    height: 3px;
    background: rgba(0, 174, 239, 0.8);
    border-radius: 50%;
    animation: float 12s linear infinite;
}

/* Particle animation */
@keyframes float {
    from { transform: translateY(0); opacity: 1; }
    to { transform: translateY(-200px); opacity: 0; }
}

/* Fade-in */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Banner neon glow */
.banner-img {
    border-radius: 16px;
    box-shadow: 0 0 25px rgba(0, 174, 239, 0.55);
    animation: glowPulse 3s infinite alternate;
}

@keyframes glowPulse {
    from { box-shadow: 0 0 15px rgba(0, 174, 239, 0.4); }
    to { box-shadow: 0 0 35px rgba(0, 174, 239, 0.9); }
}

/* Neon divider */
.neon-divider {
    height: 3px;
    width: 90%;
    margin: 10px auto 25px auto;
    background: linear-gradient(90deg,
        var(--accent-color),
        var(--primary-color),
        var(--secondary-color)
    );
    border-radius: 4px;
    animation: glowMove 3s linear infinite;
}

@keyframes glowMove {
    0% { filter: drop-shadow(0 0 4px var(--primary-color)); }
    50% { filter: drop-shadow(0 0 10px var(--secondary-color)); }
    100% { filter: drop-shadow(0 0 4px var(--accent-color)); }
}

/* Search bar neon glow */
.gr-text-input input {
    background-color: #11263F !important;
    color: var(--text-color) !important;
    border: 1px solid var(--primary-color) !important;
    box-shadow: 0 0 12px rgba(0, 174, 239, 0.45);
}

/* BUTTON BASE STYLE */
button {
    background-color: var(--secondary-color) !important;
    color: var(--text-color) !important;
    border-radius: 8px !important;
    border: 2px solid var(--primary-color) !important;
    transition: all 0.25s ease !important;
}

/* BUTTON HOVER NEON GLOW */
button:hover {
    box-shadow: 0 0 22px var(--primary-color) !important;
    border-color: var(--primary-color) !important;
    transform: translateY(-3px) !important;
}
"""


app = gr.Blocks(css=custom_css)

species_options = [
    f"{row['common_Name']} ({row['species_name']})"
    for _, row in df.iterrows()
]

def autocomplete_species(query):
    if not query:
        return gr.update(visible=False, choices=[])

    q = query.lower().strip()

    matches = df[
        df["species_name"].str.lower().str.contains(q, na=False)
        | df["common_Name"].str.lower().str.contains(q, na=False)
    ]

    if matches.empty:
        return gr.update(visible=False, choices=[])

    options = [
        f"{row['common_Name']} ({row['species_name']})"
        for _, row in matches.iterrows()
    ]

    return gr.update(visible=True, choices=options)

with app:

    # PARTICLE BACKGROUND (must be first)
    gr.HTML(
        """
        <div class="particles">
        """ +
        "\n".join([
            f'<div class="particle" style="left:{__import__("random").randint(0,100)}%; top:{__import__("random").randint(0,100)}%; animation-delay:{__import__("random").uniform(0,12)}s;"></div>'
            for _ in range(300)
        ]) +
        """
        </div>
        """
    )

    # BANNER (only once)
    gr.HTML("""
    <div style="text-align:center; margin-bottom: 25px;">
        <img class="banner-img" src="https://i.imgur.com/H6mWX4Z.png"
             style="width:100%; max-width:1850px;">
        <div class="neon-divider"></div>
    </div>
    """)

    search_input = gr.Textbox(
        label="Search species",
        placeholder="Type species name…"
    )

    species_dropdown = gr.Dropdown(
        label="Select species",
        choices=[],
        visible=False
    )

    name_output = gr.Markdown()

    gauge_group = gr.Group(visible=False)
    with gauge_group:
        gauge_output = gr.Plot()

    report_output = gr.Markdown()

    search_input.change(
        fn=autocomplete_species,
        inputs=search_input,
        outputs=species_dropdown
    )

    species_dropdown.change(
        fn=load_species,
        inputs=species_dropdown,
        outputs=[name_output, gauge_output, gauge_group, report_output]
    )

    # TOP SCORING SPECIES TOGGLE BUTTON
    top_visible = gr.State(False)
    show_top_btn = gr.Button("Top Scoring Species")

    top_section = gr.Group(visible=False)
    with top_section:
        gr.Markdown("## Top Scoring Species")
        top_table = df.sort_values("zoonointel_score", ascending=False)
        gr.Dataframe(top_table)

    def toggle_top(current):
        new_state = not current
        return new_state, gr.update(visible=new_state)

    show_top_btn.click(
        fn=toggle_top,
        inputs=top_visible,
        outputs=[top_visible, top_section]
    )


app.launch(server_name="0.0.0.0", server_port=10000)
