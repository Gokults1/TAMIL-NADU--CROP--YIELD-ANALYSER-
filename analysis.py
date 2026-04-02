import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os

print("=" * 60)
print("  TAMIL NADU CROP YIELD ANALYSER")
print("  By Gokul T S | Ponjesly College of Engineering")
print("=" * 60)

# ── 1. LOAD CSV ──────────────────────────────────────────────
csv_file = "Tamilnadu agriculture yield data.csv"
if not os.path.exists(csv_file):
    print(f"\nERROR: CSV file not found!")
    print(f"Make sure '{csv_file}' is in the same folder as this script.")
    exit()

df = pd.read_csv(csv_file)
print(f"\n✓ Data loaded successfully!")
print(f"  Total records : {len(df)}")
print(f"  Columns       : {list(df.columns)}")

# Clean column names (strip spaces)
df.columns = df.columns.str.strip()

# Rename for easy use
df.rename(columns={
    df.columns[0]: 'State',
    df.columns[1]: 'District',
    df.columns[2]: 'Year',
    df.columns[3]: 'Season',
    df.columns[4]: 'Crop',
    df.columns[5]: 'Area',
    df.columns[6]: 'Production'
}, inplace=True)

# Drop rows with missing production
df = df.dropna(subset=['Production', 'Area'])
df['Production'] = pd.to_numeric(df['Production'], errors='coerce')
df['Area'] = pd.to_numeric(df['Area'], errors='coerce')
df = df.dropna(subset=['Production', 'Area'])

print(f"  Clean records : {len(df)}")

# ── 2. SAVE TO SQLITE DATABASE ────────────────────────────────
conn = sqlite3.connect("crop_yield.db")
df.to_sql("crops", conn, if_exists="replace", index=False)
print(f"\n✓ Data saved to SQLite database (crop_yield.db)")

# ── 3. SQL QUERIES & ANALYSIS ─────────────────────────────────

# Query 1: Top 10 crops by total production
q1 = pd.read_sql_query("""
    SELECT Crop, ROUND(SUM(Production), 0) as Total_Production
    FROM crops
    GROUP BY Crop
    ORDER BY Total_Production DESC
    LIMIT 10
""", conn)
print(f"\n📊 Query 1: Top 10 Crops by Total Production")
print(q1.to_string(index=False))

# Query 2: Top 10 most productive districts
q2 = pd.read_sql_query("""
    SELECT District, ROUND(SUM(Production), 0) as Total_Production
    FROM crops
    GROUP BY District
    ORDER BY Total_Production DESC
    LIMIT 10
""", conn)
print(f"\n📊 Query 2: Top 10 Most Productive Districts")
print(q2.to_string(index=False))

# Query 3: Production trend by year
q3 = pd.read_sql_query("""
    SELECT Year, ROUND(SUM(Production), 0) as Total_Production
    FROM crops
    GROUP BY Year
    ORDER BY Year ASC
""", conn)
print(f"\n📊 Query 3: Year-wise Total Production Trend")
print(q3.to_string(index=False))

# Query 4: Top crops by season
q4 = pd.read_sql_query("""
    SELECT Season, Crop, ROUND(SUM(Production), 0) as Total_Production
    FROM crops
    GROUP BY Season, Crop
    ORDER BY Season, Total_Production DESC
    LIMIT 20
""", conn)
print(f"\n📊 Query 4: Top Crops by Season")
print(q4.to_string(index=False))

# Query 5: Most cultivated crops by area
q5 = pd.read_sql_query("""
    SELECT Crop, ROUND(SUM(Area), 0) as Total_Area
    FROM crops
    GROUP BY Crop
    ORDER BY Total_Area DESC
    LIMIT 10
""", conn)
print(f"\n📊 Query 5: Top 10 Crops by Cultivation Area")
print(q5.to_string(index=False))

conn.close()

# ── 4. VISUALIZATIONS ─────────────────────────────────────────
os.makedirs("charts", exist_ok=True)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle("Tamil Nadu Crop Yield Analysis", fontsize=18, fontweight='bold', color='#1A5276')
plt.subplots_adjust(hspace=0.5, wspace=0.4)

# Chart 1: Top 10 crops by production
ax1 = axes[0, 0]
ax1.barh(q1['Crop'][::-1], q1['Total_Production'][::-1], color='#2ECC71')
ax1.set_title('Top 10 Crops by Production', fontweight='bold')
ax1.set_xlabel('Total Production')
ax1.tick_params(axis='y', labelsize=8)

# Chart 2: Top 10 districts
ax2 = axes[0, 1]
ax2.barh(q2['District'][::-1], q2['Total_Production'][::-1], color='#3498DB')
ax2.set_title('Top 10 Productive Districts', fontweight='bold')
ax2.set_xlabel('Total Production')
ax2.tick_params(axis='y', labelsize=8)

# Chart 3: Year-wise trend
ax3 = axes[0, 2]
ax3.plot(q3['Year'], q3['Total_Production'], color='#E74C3C', marker='o', linewidth=2)
ax3.set_title('Production Trend Over Years', fontweight='bold')
ax3.set_xlabel('Year')
ax3.set_ylabel('Total Production')
ax3.tick_params(axis='x', rotation=45, labelsize=7)

# Chart 4: Top crops by area
ax4 = axes[1, 0]
ax4.bar(q5['Crop'][:5], q5['Total_Area'][:5], color='#9B59B6')
ax4.set_title('Top 5 Crops by Cultivation Area', fontweight='bold')
ax4.set_xlabel('Crop')
ax4.set_ylabel('Total Area')
ax4.tick_params(axis='x', rotation=30, labelsize=8)

# Chart 5: Season-wise production pie
season_data = df.groupby('Season')['Production'].sum().reset_index()
ax5 = axes[1, 1]
ax5.pie(season_data['Production'], labels=season_data['Season'],
        autopct='%1.1f%%', startangle=90,
        colors=['#F39C12', '#27AE60', '#2980B9', '#8E44AD', '#E74C3C'])
ax5.set_title('Production by Season', fontweight='bold')

# Chart 6: Top 5 crops comparison (area vs production)
ax6 = axes[1, 2]
top5 = q1.head(5)
x = range(len(top5))
ax6.bar(x, top5['Total_Production'], color='#1ABC9C')
ax6.set_xticks(x)
ax6.set_xticklabels(top5['Crop'], rotation=30, ha='right', fontsize=8)
ax6.set_title('Top 5 Crops Production Comparison', fontweight='bold')
ax6.set_ylabel('Total Production')

plt.savefig("charts/crop_analysis.png", dpi=150, bbox_inches='tight')
print(f"\n✓ Charts saved to charts/crop_analysis.png")
print(f"\n{'=' * 60}")
print(f"  PROJECT COMPLETE!")
print(f"  Files created:")
print(f"  - crop_yield.db   (SQLite database)")
print(f"  - charts/crop_analysis.png  (All visualizations)")
print(f"{'=' * 60}")
