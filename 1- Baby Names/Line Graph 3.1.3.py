import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

def load_name_data(folder_path):
    data = {}
    for year in range(1900, 2023+1):
        file_path = os.path.join(folder_path, f'yob{year}.txt')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, names=['name', 'gender', 'count'])
            data[year] = df
    return data

def get_name_counts(name, data, start_year):
    counts = []
    for year in range(start_year, 2023+1):
        if year in data:
            count = data[year][data[year]['name'] == name]['count'].sum()
            counts.append(count)
        else:
            counts.append(0)
    return counts

def plot_individual_graphs(all_shows, name_data, selected_shows=None, show_dotted=False):
    fig, axs = plt.subplots(5, 2, figsize=(8.3, 11.7))
    axs = axs.flatten()
    colors = ['red', 'darkorange', 'green', 'royalblue', 'navy', 'purple']

    for i, show in enumerate(all_shows):
        if selected_shows and show['tv_show_name'] not in selected_shows:
            continue

        start_year = 1970 if show['tv_show_name'] == "Friends" else 1990
        ax = axs[i]

        for j, character in enumerate(show['characters']):
            first_name = character.split()[0]
            counts = get_name_counts(first_name, name_data, start_year)
            counts = [max(c, 1) for c in counts]

            release_year = show['release_year']
            pre_release_counts = counts[:release_year - start_year + 1]
            post_release_counts = counts[release_year - start_year:]

            if show_dotted:
                ax.plot(range(start_year, release_year + 1), pre_release_counts, linestyle=':', color=colors[j % len(colors)])
                ax.plot(range(release_year, 2023+1), post_release_counts, linestyle='-', color=colors[j % len(colors)])
                ax.scatter(release_year, counts[release_year - start_year], color=colors[j % len(colors)], marker='o', s=60, zorder=5)
            else:
                ax.plot(range(start_year, 2023+1), counts, color=colors[j % len(colors)])

            ax.annotate(first_name, xy=(2023, counts[-1]), xytext=(5, 0), textcoords='offset points',
                        color=colors[j % len(colors)], fontsize=6.5, fontweight='bold')

        ax.set_title(f"{show['tv_show_name']} ({release_year})", fontsize=10)
        ax.set_yscale('log')
        ax.grid(True)

    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])

    plt.suptitle("TV Show Character Name Popularity (1990-2023)", fontsize=14)
    fig.tight_layout()
    plt.savefig("individual_tv_shows_A4_grid.pdf")
    plt.show()

def plot_average_popularity(all_shows, name_data, file_name, selected_shows=None, show_dotted=True):
    plt.figure(figsize=(8, 4))
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown', 'palevioletred']

    all_show_averages = []
    handles = []
    labels = []

    for i, show in enumerate(all_shows):
        if selected_shows and show['tv_show_name'] not in selected_shows:
            continue

        start_year = 1990
        show_counts = []

        for character in show['characters']:
            first_name = character.split()[0]
            counts = get_name_counts(first_name, name_data, start_year)
            show_counts.append(counts)

        show_average = np.mean(show_counts, axis=0) if show_counts else np.zeros(len(range(start_year, 2023+1)))
        all_show_averages.append(show_average)

        release_year = show['release_year']
        pre_release_average = show_average[:release_year - start_year + 1]
        post_release_average = show_average[release_year - start_year:]

        if show_dotted:
            plt.plot(range(start_year, release_year + 1), pre_release_average, linestyle=':', color=colors[i])
            plt.plot(range(release_year, 2023+1), post_release_average, linestyle='-', color=colors[i])
            plt.scatter(release_year, show_average[release_year - start_year], color=colors[i], marker='o', s=100, zorder=5)
        else:
            plt.plot(range(start_year, 2023+1), show_average, label=f"{show['tv_show_name']}: {show['release_year']}", color=colors[i])

        handles.append(plt.Line2D([0], [0], color=colors[i], linestyle='-'))
        labels.append(f"{show['tv_show_name']} ({show['release_year']})")

    overall_average = np.mean(all_show_averages, axis=0)
    plt.plot(range(1990, 2023+1), overall_average, label="Overall Average (All 50 Names)", color='black', linestyle='-', linewidth=2.3, alpha=0.7)

    handles.append(plt.Line2D([0], [0], color='black', linestyle='-', linewidth=2.5))
    labels.append("Overall Average (All 50 Names)")

    plt.legend(handles=handles, labels=labels, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.title("Average Character Name Popularity Per Show (1990-2023)")
    plt.xlabel('Year')
    plt.ylabel('Number of Babies')
    plt.yscale('log')
    plt.grid(True)
    plt.tight_layout()

    plt.text(1, 0.02, f"File: {file_name}", horizontalalignment='right', verticalalignment='bottom',
             transform=plt.gca().transAxes, fontsize=6, color='black')

    plt.show()

def main_plot(all_shows, name_data, file_name, plot_averages=False, plot_individuals=False, selected_shows=None,
              selected_names=None, show_dotted=False):
    if plot_individuals:
        plot_individual_graphs(all_shows, name_data, selected_shows, show_dotted)

    if plot_averages:
        plot_average_popularity(all_shows, name_data, file_name, selected_shows)

if __name__ == "__main__":
    folder_path = r'C:\Users\ybars\OneDrive - huji.ac.il\HUJI Documents Shana BET\MATAR Bet\Data Mining 47717\babynames text files'
    name_data = load_name_data(folder_path)

    def load_shows_from_file(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    shows_file_path = r'C:\Users\ybars\PycharmProjects\datamining\DM_Names_new_approach\output\tv_shows_new_release.json'
    all_shows = load_shows_from_file(shows_file_path)

    file_name = "line_graph_A4_vertical.pdf"

    main_plot(all_shows, name_data, file_name, plot_averages=True, plot_individuals=True, show_dotted=True)
    main_plot(all_shows, name_data, file_name, plot_averages=True, plot_individuals=False)  # For average graph
