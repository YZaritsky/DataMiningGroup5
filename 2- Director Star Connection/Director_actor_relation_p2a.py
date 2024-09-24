import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = './data/imdb-movies-dataset.csv'
df = pd.read_csv(file_path)

# List of directors
directors = [
    "Clint Eastwood", "Martin Scorsese", "Francis Ford Coppola", "Tim Burton",
    "Renny Harlin", "Alfred Hitchcock", "Ron Howard", "Ridley Scott",
    "Steven Spielberg", "Woody Allen", "Robert Zemeckis", "Steven Soderbergh"
]

# Step 1: Create a new DataFrame with 'Director', 'Cast', and 'Year' columns where 'Cast' is split into individual actors
df_exploded = df[['Director', 'Cast', 'Year']].copy()
df_exploded['Cast'] = df_exploded['Cast'].str.split(', ')
df_exploded = df_exploded.explode('Cast')

# Step 2: Filter the DataFrame for the directors of interest
df_filtered = df_exploded[df_exploded['Director'].isin(directors)]

# Step 3: Generate the plots for each director
for director in directors:
    df_director = df_filtered[df_filtered['Director'] == director]

    # Identify the top 3 actors who have worked most frequently with this director
    top_actors = df_director['Cast'].value_counts().head(3).index.tolist()

    # Create a plot for each director
    plt.figure(figsize=(10, 6))

    for actor in top_actors:
        df_actor = df_director[df_director['Cast'] == actor].copy()

        # Group by 5-year intervals
        df_actor.loc[:, 'Year_Group'] = (df_actor['Year'] // 5) * 5
        df_grouped = df_actor.groupby('Year_Group').size()

        # Plotting
        plt.plot(df_grouped.index, df_grouped.values, label=actor)

    plt.xlabel('5-Year Intervals')
    plt.ylabel('Number of Films')
    plt.title(f'Film Counts for Top 3 Actors with {director}')
    plt.legend()
    plt.grid(True)

    # Save the plot
    plt.savefig(f'./output/shellys_request2/{director}_film_counts.png', dpi=300, bbox_inches='tight')
    plt.show()