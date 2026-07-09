from google.colab import files
uploaded = files.upload()

file_name = list(uploaded.keys())[0]
df = pd.read_csv(file_name)

df.head()

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
            "text": "<b>ZoonoIntel Score</b>",
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

def search_species(query):
    if not query:
        return "", None, gr.update(visible=False), "Type a species name or common name to search."

    q = query.strip()

    exact_common = df[df["common_Name"].str.lower() == q.lower()]
    if not exact_common.empty:
        row = exact_common.iloc[0]
    else:
        exact_scientific = df[df["species_name"].str.lower() == q.lower()]
        if not exact_scientific.empty:
            row = exact_scientific.iloc[0]
        else:
            partial = df[
                df["species_name"].str.contains(q, case=False, na=False)
                | df["common_Name"].str.contains(q, case=False, na=False)
            ]
            if partial.empty:
                return "", None, gr.update(visible=False), "No species found."
            row = partial.iloc[0]

    score = row["zoonointel_score"]
    gauge = create_gauge(score)

    name_md = f"## {row['species_name']} ({row.get('common_Name', 'No common name')})"

    d1 = driver_name_map.get(row.get("top_driver_1", ""), row.get("top_driver_1", ""))
    d2 = driver_name_map.get(row.get("top_driver_2", ""), row.get("top_driver_2", ""))
    d3 = driver_name_map.get(row.get("top_driver_3", ""), row.get("top_driver_3", ""))

    report = f"""
### Taxonomy
**Order:** {row['order']}<br>
**Family:** {row['family']}

----

## **ZoonoIntel Prediction**
**Score:** {score} / 100
**Risk Tier:** {row['risk_tier']}

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
    --primary-color: #00AEEF;
    --secondary-color: #FF7A00;
    --accent-color: #00C853;
    --background-color: #0A1A2F;
    --text-color: #FFFFFF;
    --font-family: 'Orbitron', sans-serif;
}

/* Global font */
* {
    font-family: var(--font-family) !important;
}

/* Background + fade-in */
.gradio-container {
    background: linear-gradient(135deg, #0A1A2F 0%, #0F2A45 40%, #0A1A2F 100%) !important;
    color: var(--text-color) !important;
    animation: fadeIn 1.2s ease-in-out;
}

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

with gr.Blocks(title="ZoonoIntel") as app:

    gr.HTML("""
    <div style="text-align:center; margin-bottom: 25px;">
        <img class="banner-img" src="https://i.imgur.com/H6mWX4Z.png"
             style="width:100%; max-width:1850px;">
        <div class="neon-divider"></div>
    </div>
    """)

    search_input = gr.Textbox(
        label="Search species name",
        placeholder="Type species name…"
    )

    name_output = gr.Markdown()

    gauge_group = gr.Group(visible=False)
    with gauge_group:
        gauge_output = gr.Plot()

    report_output = gr.Markdown()

    search_input.change(
        fn=search_species,
        inputs=search_input,
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



app.launch(share=True, css=custom_css)