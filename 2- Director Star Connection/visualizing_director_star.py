import pandas as pd
import matplotlib.pyplot as plt
import time

# Load the CSV file
file_path = './data/movies.csv'  # Update with your actual file path
print("Loading CSV file...")
start_time = time.time()
movies_df = pd.read_csv(file_path)
print(f"CSV file loaded successfully in {time.time() - start_time:.2f} seconds.")

# Display the first few rows of the dataframe
print("First few rows of the dataframe:")
print(movies_df.head())

# Group by director and star, and count the occurrences
print("Grouping by director and star...")
start_time = time.time()
director_star_count = movies_df.groupby(['director', 'star']).size().unstack(fill_value=0)
print(f"Grouping completed in {time.time() - start_time:.2f} seconds. Here is a preview of the grouped data:")
print(director_star_count.head())

# Sum the number of movies for each director and select the top 100
top_directors = director_star_count.sum(axis=1).nlargest(100).index
print(f"Top 100 directors selected based on the number of movies.")

# Filter the data to include only the top 100 directors
director_star_count_top = director_star_count.loc[top_directors]

# Plotting the data
print("Plotting the data...")
start_time = time.time()
fig, ax = plt.subplots(figsize=(20, 12))  # Increase the figure size
director_star_count_top.plot(kind='bar', stacked=True, ax=ax)
ax.set_title('Number of Movies Directed by Top 100 Directors with Specific Stars')
ax.set_xlabel('Directors')
ax.set_ylabel('Number of Movies')
ax.legend(title='Stars', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45, ha='right')
plt.subplots_adjust(bottom=0.3)  # Adjust the bottom margin
print(f"Plotting completed in {time.time() - start_time:.2f} seconds.")

# Save the plot as an image file
plot_path = 'director_star_count_top_100_plot.png'
print(f"Saving the plot as an image file: {plot_path}")
start_time = time.time()
plt.savefig(plot_path)
print(f"Plot saved successfully in {time.time() - start_time:.2f} seconds.")
plt.show()

print("Script execution completed.")
