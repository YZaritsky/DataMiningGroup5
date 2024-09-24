import pandas as pd
import ast
import matplotlib.pyplot as plt

# Load the datasets
frequent_collab_df = pd.read_csv('./output/frequent_director_actor_collaborations.csv')
non_frequent_collab_df = pd.read_csv('./output/non_frequent_director_actor_collaborations.csv')
box_office_df = pd.read_csv('./data/top_10_box_office_movies_1977_2023.csv')

# Clean the 'Gross' field in the box office dataset to remove dollar signs and commas, and convert to numeric
box_office_df['Gross'] = box_office_df['Gross'].replace({'\$': '', ',': ''}, regex=True).astype(float)

# Step 1: Filter frequent collaborations where the movies are in the top box office
frequent_in_box_office = []
for i, row in frequent_collab_df.iterrows():
    director = row['Director']
    for movie in ast.literal_eval(row['Movies']):
        movie_match = box_office_df[box_office_df['Title'].str.contains(movie, case=False, na=False, regex=False)]
        if not movie_match.empty:
            for _, matched_row in movie_match.iterrows():
                frequent_in_box_office.append({'Director': director, 'Title': matched_row['Title'], 'Gross': matched_row['Gross'], 'Frequent': True})

# Convert to dataframe
frequent_in_box_office_df = pd.DataFrame(frequent_in_box_office)

# Step 2: Find non-frequent collaborations that are in the top box office
non_frequent_in_box_office = []
for i, row in non_frequent_collab_df.iterrows():
    director = row['Director']
    for movie in ast.literal_eval(row['Movies']):
        movie_match = box_office_df[box_office_df['Title'].str.contains(movie, case=False, na=False, regex=False)]
        if not movie_match.empty:
            for _, matched_row in movie_match.iterrows():
                non_frequent_in_box_office.append({'Director': director, 'Title': matched_row['Title'], 'Gross': matched_row['Gross'], 'Frequent': False})

# Convert to dataframe
non_frequent_in_box_office_df = pd.DataFrame(non_frequent_in_box_office)

# Step 3: Combine the datasets (frequent and non-frequent)
combined_box_office_df = pd.concat([frequent_in_box_office_df, non_frequent_in_box_office_df], ignore_index=True)

# Step 4: Filter the directors who have at least 2 frequent movies and 1 non-frequent movie in the box office
director_movie_counts = combined_box_office_df.groupby(['Director', 'Frequent']).size().unstack(fill_value=0)
top_directors = director_movie_counts[(director_movie_counts[True] >= 2) & (director_movie_counts[False] >= 1)].index

# Filter combined dataframe for top directors
top_directors_df = combined_box_office_df[combined_box_office_df['Director'].isin(top_directors)]

# Step 5: Identify the top 15 directors with the highest average gross (considering both frequent and non-frequent)
# Calculate the overall average gross for each director
directors_average_gross = top_directors_df.groupby('Director')['Gross'].mean()

# Get the top 15 directors by average gross
top_15_directors = directors_average_gross.nlargest(15).index

# Filter the dataframe to only include the top 15 directors
top_15_directors_df = top_directors_df[top_directors_df['Director'].isin(top_15_directors)]

# Convert the gross to millions of dollars for better readability
top_15_directors_df['Gross'] = top_15_directors_df['Gross'] / 1_000_000

# Step 6: Calculate the average gross for frequent and non-frequent movies for each top 15 director (in millions)
average_gross_by_type_top_15 = top_15_directors_df.groupby(['Director', 'Frequent'])['Gross'].mean().unstack()

# Step 7: Create a bar plot comparing the average gross for each top 15 director
# Use 'skyblue' for Frequent and 'lightgreen' for Non-Frequent to match with the summary plot
average_gross_by_type_top_15.plot(kind='bar', figsize=(10,6), color=['#e74c3c', '#3498db'])
plt.title('Average Gross Comparison: Frequent vs Non-Frequent Collaborations (Top 15 Directors)')
plt.ylabel('Average Gross (Million $)')
plt.xlabel('Director')
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# Step 8: Summary Visualization for Top 15 Directors
# Instead of recalculating the average for all movies, take the mean of the averages from Step 6
frequent_avg = average_gross_by_type_top_15[True].mean()
non_frequent_avg = average_gross_by_type_top_15[False].mean()

# Create a DataFrame for the summary visualization
summary_df = pd.DataFrame({
    'Non-Frequent': [non_frequent_avg],
    'Frequent': [frequent_avg]
    
})

# Create a summary bar plot comparing overall frequent vs non-frequent collaborations (Top 15 directors)
plt.figure(figsize=(8, 6))
ax = summary_df.plot(kind='bar', color=['#e74c3c', '#3498db'], legend=False)  # Make sure colors match
plt.title('Overall Average Gross: Non-Frequent vs Frequent Collaborations (Top 15 Directors)')
plt.ylabel('Average Gross (Million $)')
plt.xticks([0], ['Non-Frequent vs Frequent'], rotation=0)

# Add the labels (average gross values) on top of each bar
for i in ax.containers:
    ax.bar_label(i, fmt='%.2f', label_type='edge')

plt.tight_layout()
plt.show()
