# AI Parking Intelligence System

## Problem Statement

Poor Visibility on Parking-Induced Congestion

Illegal parking near commercial areas, metro stations, and major junctions causes traffic congestion and reduces road capacity. Current enforcement is reactive and lacks hotspot identification.

## Solution

AI-driven Parking Intelligence System that:

* Detects parking hotspots using DBSCAN clustering
* Calculates Congestion Impact Score
* Identifies Priority Enforcement Zones
* Predicts Risk Level of parking violations
* Provides interactive hotspot visualization

## Technologies Used

* Python
* Pandas
* Scikit-Learn
* DBSCAN
* Streamlit
* Folium
* Plotly

## Dataset

115,400 validated parking violation records from Bengaluru.

## Results

* 51 parking hotspots detected
* Congestion Impact Score generated
* High-risk enforcement zones identified
* Interactive dashboard developed

## How to Run

```bash
pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```
