import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
import plotly.express as px
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Parking Intelligence System",
    page_icon="🚗",
    layout="wide"
)

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    BASE_DIR / "data" / "final_dataset.csv"
)

hotspots = pd.read_csv(
    BASE_DIR / "data" / "hotspot_locations.csv"
)

model = joblib.load(
    BASE_DIR / "models" / "risk_model.pkl"
)

# ==========================================
# FEATURE IMPORTANCE
# ==========================================

feature_importance = pd.DataFrame({
    "Feature": [
        "Vehicle Score",
        "Violation Score",
        "Junction Factor",
        "Hour",
        "Month"
    ],
    "Importance": [
        0.508242,
        0.304766,
        0.178152,
        0.006465,
        0.002376
    ]
})
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# ==========================================
# HEADER
# ==========================================

st.title("🚗 AI Parking Intelligence System")



# ==========================================
# SIDEBAR
# ==========================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Nearest Parking Finder",
        "Hotspot Map",
        "Top Hotspots",
        "Feature Importance",
        "Risk Prediction",
        "Enforcement Recommendations",
        "System Architecture"
    ]
)

# ==========================================
# OVERVIEW
# ==========================================

if page == "Overview":
    st.markdown("""
    

    AI-powered parking hotspot detection and congestion impact analysis.

    **Features**
    - Hotspot Detection using DBSCAN
    - Congestion Impact Scoring
    - Risk Prediction
    - Enforcement Recommendations
    """)

    # ==========================================
    # KPI CARDS
    # ==========================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Violations",
            f"{len(df):,}"
        )

    with col2:
        st.metric(
            "Hotspots",
            df["cluster"].nunique() - 1
        )

    with col3:
        st.metric(
            "Police Stations",
            df["police_station"].nunique()
        )

    with col4:
        st.metric(
            "Critical Cases",
            len(df[df["risk_level"] == "Critical"])
        )

    st.divider()

    st.header("📊 Project Overview")

    risk_counts = df["risk_level"].value_counts()

    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title="Risk Level Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Top 10 Hotspots")

    st.dataframe(
        hotspots.sort_values(
            by="impact_score",
            ascending=False
        ).head(10),
        use_container_width=True
    )

# ==========================================
# HOTSPOT MAP
# ==========================================

elif page == "Hotspot Map":

    st.header("🌍 Bengaluru Parking Hotspots")

    m = folium.Map(
        location=[
            hotspots["latitude"].mean(),
            hotspots["longitude"].mean()
        ],
        zoom_start=11
    )

    for _, row in hotspots.iterrows():

        color = "green"

        if row["impact_score"] > 10:
            color = "red"

        elif row["impact_score"] > 8:
            color = "orange"

        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=f"""
            <b>Police Station:</b> {row['police_station']}<br>
            <b>Impact Score:</b> {row['impact_score']:.2f}
            """,
            icon=folium.Icon(color=color)
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=700
    )

# ==========================================
# TOP HOTSPOTS
# ==========================================

elif page == "Top Hotspots":

    st.header("🔥 Top Parking Hotspots")

    ranked = hotspots.sort_values(
        by="impact_score",
        ascending=False
    )

    st.dataframe(
        ranked,
        use_container_width=True
    )

    fig = px.bar(
        ranked.head(10),
        x="police_station",
        y="impact_score",
        title="Top 10 Hotspots"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# FEATURE IMPORTANCE
# ==========================================

elif page == "Feature Importance":

    st.header("📈 Feature Importance")

    fig = px.bar(
        feature_importance,
        x="Feature",
        y="Importance",
        title="Factors Influencing Congestion Risk"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("""
### Key Findings

- Vehicle Type contributes most to congestion.
- Violation Severity is the second most important factor.
- Junction proximity significantly increases impact.
- Hour and Month have minimal effect.
""")

# ==========================================
# RISK PREDICTION
# ==========================================

elif page == "Risk Prediction":

    st.header("🤖 Risk Prediction")

    vehicle_score = st.slider(
        "Vehicle Score",
        1,
        7,
        3
    )

    violation_score = st.slider(
        "Violation Severity",
        1,
        6,
        3
    )

    junction_factor = st.selectbox(
        "Near Junction?",
        [1, 2]
    )

    hour = st.slider(
        "Hour",
        0,
        23,
        12
    )

    month = st.slider(
        "Month",
        1,
        12,
        6
    )

    if st.button("Predict Risk"):

        prediction = model.predict([
            [
                hour,
                month,
                vehicle_score,
                violation_score,
                junction_factor
            ]
        ])

        risk = prediction[0]

        if risk == "Critical":
            st.error(f"Predicted Risk: {risk}")

        elif risk == "High":
            st.warning(f"Predicted Risk: {risk}")

        elif risk == "Medium":
            st.info(f"Predicted Risk: {risk}")

        else:
            st.success(f"Predicted Risk: {risk}")

# ==========================================
# ENFORCEMENT RECOMMENDATIONS
# ==========================================

elif page == "Enforcement Recommendations":

    st.header("🚔 Enforcement Priority Zones")

    recommendations = hotspots.sort_values(
        by="impact_score",
        ascending=False
    )

    st.dataframe(
        recommendations.head(10),
        use_container_width=True
    )

    top_zone = recommendations.iloc[0]

    st.error(
        f"""
Highest Priority Area

Police Station: {top_zone['police_station']}

Impact Score: {top_zone['impact_score']:.2f}
"""
    )

# ==========================================
# SYSTEM ARCHITECTURE
# ==========================================

elif page == "System Architecture":

    st.header("⚙️ System Workflow")

    st.markdown("""
### AI Parking Intelligence Pipeline

Parking Violation Data

⬇️

Data Cleaning

⬇️

Feature Engineering

⬇️

DBSCAN Hotspot Detection

⬇️

Congestion Impact Score

⬇️

Risk Classification

⬇️

Random Forest Model

⬇️

Targeted Enforcement Recommendations
""")

    st.success(
        "AI discovered 51 parking hotspots from 115,400 validated violations."
    )

    st.subheader("Project Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Violations",
            "115,400"
        )

    with col2:
        st.metric(
            "Hotspots Found",
            "51"
        )

    with col3:
        st.metric(
            "High + Critical Risk",
            "7,338"
        )


# ==========================================
# NEAREST PARKING FINDER
# ==========================================

elif page == "Nearest Parking Finder":

    st.header("🅿️ Find Nearest Parking Hotspots")

    # Initialize session state
    if "nearest_spots" not in st.session_state:
        st.session_state.nearest_spots = None

    # Remove invalid coordinates
    parking_data = hotspots.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    col1, col2 = st.columns(2)

    with col1:
        user_lat = st.number_input(
            "Your Latitude",
            value=12.9716,
            format="%.6f"
        )

    with col2:
        user_lon = st.number_input(
            "Your Longitude",
            value=77.5946,
            format="%.6f"
        )

    search_btn = st.button(
        "Find Nearest Parking Spots",
        type="primary"
    )

    if search_btn:

        try:

            parking_data["distance_km"] = parking_data.apply(
                lambda row: haversine(
                    float(user_lat),
                    float(user_lon),
                    float(row["latitude"]),
                    float(row["longitude"])
                ),
                axis=1
            )

            st.session_state.nearest_spots = (
                parking_data
                .sort_values("distance_km")
                .head(5)
                .reset_index(drop=True)
            )

        except Exception as e:
            st.error(f"Error: {e}")

    # Show results even after rerun
    if st.session_state.nearest_spots is not None:

        nearest = st.session_state.nearest_spots

        st.subheader("📍 Top 5 Nearest Parking Hotspots")

        st.dataframe(
            nearest[
                [
                    "police_station",
                    "impact_score",
                    "distance_km"
                ]
            ],
            use_container_width=True
        )

        # Create map
        m = folium.Map(
            location=[float(user_lat), float(user_lon)],
            zoom_start=13
        )

        # User marker
        folium.Marker(
            [float(user_lat), float(user_lon)],
            popup="Your Location",
            tooltip="Your Location",
            icon=folium.Icon(color="blue")
        ).add_to(m)

        # Parking markers
        for _, row in nearest.iterrows():

            popup_text = f"""
            <b>{row['police_station']}</b><br>
            Impact Score: {row['impact_score']:.2f}<br>
            Distance: {row['distance_km']:.2f} km
            """

            folium.Marker(
                [
                    float(row["latitude"]),
                    float(row["longitude"])
                ],
                popup=popup_text,
                tooltip=row["police_station"],
                icon=folium.Icon(color="green")
            ).add_to(m)

        st_folium(
            m,
            width=None,
            height=600,
            use_container_width=True
        )