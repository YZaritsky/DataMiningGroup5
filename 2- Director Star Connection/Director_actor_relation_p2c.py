import pandas as pd
import matplotlib.pyplot as plt

# Load the grouped awards data from the CSV file
awards_grouped = pd.read_csv('./output/shellys_request2c/director_awards_list.csv')

# List of directors (same as before)
directors = [
    "Clint Eastwood", "Martin Scorsese", "Francis Ford Coppola", "Tim Burton",
    "Renny Harlin", "Alfred Hitchcock", "Ron Howard", "Ridley Scott",
    "Steven Spielberg", "Woody Allen", "Robert Zemeckis", "Steven Soderbergh"
]

# Create a graph for each director
for director in directors:
    # Filter data for the current director
    df_director = awards_grouped[awards_grouped['Director'] == director].copy()

    # Convert the 'Year' column to integers, dropping any NaN values
    df_director['Year'] = pd.to_numeric(df_director['Year'], errors='coerce')
    df_director = df_director.dropna(subset=['Year'])
    df_director['Year'] = df_director['Year'].astype(int)

    # Group by 5-year intervals
    df_director['Year_Group'] = (df_director['Year'] // 5) * 5
    df_grouped = df_director.groupby('Year_Group')['Film_Count'].sum().reset_index()

    # Sort data by year
    df_grouped = df_grouped.sort_values('Year_Group')

    # Create a plot for the director
    plt.figure(figsize=(10, 6))
    plt.plot(df_grouped['Year_Group'], df_grouped['Film_Count'], marker='o')

    # Labeling the plot
    plt.xlabel('5-Year Intervals')
    plt.ylabel('Number of Awards')
    plt.title(f'Number of Awards Over Time for {director}')
    plt.grid(True)

    # Ensure the ticks on the X-axis are integers
    plt.xticks(df_grouped['Year_Group'].unique().astype(int))

    # Save the plot
    plt.savefig(f'./output/shellys_request2c/{director}_awards_over_time.png', dpi=300, bbox_inches='tight')
    plt.show()