import pandas as pd
import re
import matplotlib.pyplot as plt

# Step 1: Load the dataset (assuming the same dataset for both actors and actresses)
file_path = './data/imdb-movies-dataset.csv'
df = pd.read_csv(file_path)

# Step 2: Create a new DataFrame with 'Director', 'Cast', and 'Title' columns where 'Cast' is split into individual actors
df_exploded = df[['Director', 'Cast', 'Title']].copy()
df_exploded['Cast'] = df_exploded['Cast'].str.split(', ')
df_exploded = df_exploded.explode('Cast')

# Step 3: Count the number of times each actor has worked with each director
director_actor_count = df_exploded.groupby(['Director', 'Cast']).size().reset_index(name='Count')

# Step 4: Filter the collaborations where the actor/actress has worked with the same director at least 3 times (frequent)
frequent_collabs = director_actor_count[director_actor_count['Count'] >= 3]

# Step 4.1: Filter the collaborations where the actor/actress has worked with the same director less than 3 times (non-frequent)
non_frequent_collabs = director_actor_count[director_actor_count['Count'] < 3]

# Step 5: For each director and actor pair, list all the movies they have worked on together
collab_movies = df_exploded.groupby(['Director', 'Cast'])['Title'].apply(list).reset_index()

# Step 6: Merge the frequent collaborations with the list of movies
frequent_collab_movies = pd.merge(frequent_collabs, collab_movies, on=['Director', 'Cast'])

# Step 6.1: Merge the non-frequent collaborations with the list of movies
non_frequent_collab_movies = pd.merge(non_frequent_collabs, collab_movies, on=['Director', 'Cast'])

# Step 7: Select only the relevant columns (Director, Cast, and Movies) and rename them
frequent_collab_movies = frequent_collab_movies[['Director', 'Cast', 'Title']]
frequent_collab_movies.columns = ['Director', 'Actor/Actress', 'Movies']

non_frequent_collab_movies = non_frequent_collab_movies[['Director', 'Cast', 'Title']]
non_frequent_collab_movies.columns = ['Director', 'Actor/Actress', 'Movies']

# Step 8: Save the result to a CSV file
frequent_collab_movies.to_csv('./output/frequent_director_actor_collaborations.csv', index=False)
non_frequent_collab_movies.to_csv('./output/non_frequent_director_actor_collaborations.csv', index=False)

# Optional: Print the first few rows to check the output
print("Frequent Collaborations:\n", frequent_collab_movies.head())
print("\nNon-Frequent Collaborations:\n", non_frequent_collab_movies.head())


# Additional part to process IMDb lists and generate the plots
def process_imdb_list(file_path_txt, output_prefix):
    # Step 9: Load the text file containing the IMDB list and rankings
    with open(file_path_txt, 'r', encoding='utf-8') as file:
        imdb_actor_list = file.readlines()

    # Step 10: Extract actor names and their rankings from the text file
    actor_ranking_pattern = re.compile(r'^(\d+)\.\s([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)')

    # Dictionary to hold the actor names and their corresponding rankings
    actor_rankings = {}

    for line in imdb_actor_list:
        match = actor_ranking_pattern.match(line.strip())
        if match:
            rank = int(match.group(1))
            actor_name = match.group(2)
            actor_rankings[actor_name] = rank

    # Cross-reference the extracted actors with the earlier lists
    actors_in_common_red = set(actor_rankings.keys()) & set(frequent_collabs['Cast'])
    actors_in_common_blue = set(actor_rankings.keys()) & set(non_frequent_collabs['Cast'])

    # Step 11: Save the two lists as CSV files
    actors_same_director_df = pd.DataFrame({'Actor': list(actors_in_common_red), 'Category': 'Red'})
    actors_different_directors_df = pd.DataFrame({'Actor': list(actors_in_common_blue), 'Category': 'Blue'})
    actors_same_director_df.to_csv(f'./output/shellys_request/{output_prefix}_actors_same_director_common.csv', index=False)
    actors_different_directors_df.to_csv(f'./output/shellys_request/{output_prefix}_actors_different_directors_common.csv', index=False)

    # Step 12: Prepare the data for the plot using the rankings from the text file
    sorted_actors = sorted(actor_rankings.items(), key=lambda x: x[1])
    x_labels, y_values = zip(*sorted_actors)

    # Filter to include only actors that are in the common lists (Red or Blue)
    x_labels = [actor for actor in x_labels if actor in actors_in_common_red.union(actors_in_common_blue)]
    y_values = [actor_rankings[actor] for actor in x_labels]

    # Reverse the order of x_labels and y_values to make names ordered from right to left
    x_labels = x_labels[::-1]
    y_values = y_values[::-1]

    # Determine the colors based on the list membership
    colors = ['red' if actor in actors_in_common_red else 'blue' for actor in x_labels]

    # Step 13: Plotting the graph
    plt.figure(figsize=(10, 8))
    plt.scatter(x_labels, y_values, c=colors)

    # Adding labels and title
    plt.xticks(rotation=90)
    plt.xlabel('Actors')
    plt.ylabel('Rankings (1-100)')
    plt.title(f'{output_prefix.capitalize()} Actor Rankings Based on IMDB List')
    plt.grid(True)

    # Reverse the Y-axis so that 1 is at the top and 100 is at the bottom
    plt.gca().invert_yaxis()

    # Adding the legend
    plt.legend(handles=[
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Same director 3+ times'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Fewer than 3 times')
    ])

    # Show the plot
    plt.tight_layout()
    plt.savefig(f'./output/shellys_request/{output_prefix}_actor_rankings_plot.png', dpi=300, bbox_inches='tight')
    plt.show()


# Process both the actresses and actors lists
process_imdb_list('data/IMDB_top_100_female_actresses.txt', 'female')
process_imdb_list('data/IMDB_top_100_male_actors.txt', 'male')
