import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

def load_name_data(folder_path):
    data = {}
    for year in range(1970, 2024):
        file_path = os.path.join(folder_path, f'yob{year}.txt')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, names=['name', 'gender', 'count'])
            data[year] = df
    return data

def get_name_counts(name, data, start_year):
    counts = []
    for year in range(start_year, 2024):
        if year in data:
            count = data[year][data[year]['name'] == name]['count'].sum()
            counts.append(count)
        else:
            counts.append(0)
    return counts

def get_percentage_jump(name, data, debut_year):
    debut_count = get_name_counts(name, data, debut_year)[0]
    counts_after_debut = get_name_counts(name, data, debut_year)[1:8]
    avg_counts_after_debut = sum(counts_after_debut) / len(counts_after_debut) if counts_after_debut else 0
    if debut_count > 0:
        percentage_jump = ((avg_counts_after_debut - debut_count) / debut_count) * 100
        return percentage_jump
    else:
        return 0

def calculate_show_metrics(all_shows, name_data):
    show_metrics = {}
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown', 'palevioletred']
    for i, show in enumerate(all_shows):
        debut_year = show['release_year']
        show_name = show['tv_show_name']
        percentage_jumps = []
        debut_counts = []
        total_debut_count = 0
        total_avg_count_after = 0
        for character in show['characters']:
            first_name = character.split()[0]
            debut_count = get_name_counts(first_name, name_data, debut_year)[0]
            percentage_jump = get_percentage_jump(first_name, name_data, debut_year)
            counts_after_debut = get_name_counts(first_name, data=name_data, start_year=debut_year)[1:8]
            avg_count_after_debut = sum(counts_after_debut) / len(counts_after_debut) if counts_after_debut else 0
            if debut_count > 0:
                percentage_jumps.append(percentage_jump)
                debut_counts.append(debut_count)
                total_debut_count += debut_count
                total_avg_count_after += avg_count_after_debut
        if percentage_jumps:
            avg_percentage_jump = sum(percentage_jumps) / len(percentage_jumps)
            if total_debut_count > 0:
                total_percentage_change = ((total_avg_count_after - total_debut_count) / total_debut_count) * 100
            else:
                total_percentage_change = 0
            weighted_sum = sum(p * d for p, d in zip(percentage_jumps, debut_counts))
            weighted_avg_percentage_jump = weighted_sum / total_debut_count if total_debut_count > 0 else 0
            show_metrics[show_name] = {
                'Average Percentage Jump': avg_percentage_jump,
                'Total Percentage Change': total_percentage_change,
                'Weighted Average Percentage Jump': weighted_avg_percentage_jump,
                'Number of Names': len(percentage_jumps)
            }
        else:
            show_metrics[show_name] = {
                'Average Percentage Jump': None,
                'Total Percentage Change': None,
                'Weighted Average Percentage Jump': None,
                'Number of Names': 0
            }
    return show_metrics

def scatter_plot_linear_regression(all_shows, name_data, show_metrics):
    debut_popularities = []
    percentage_jumps = []
    name_labels = []
    show_colors = []
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'brown', 'palevioletred']
    show_name_to_color = {}
    for i, show in enumerate(all_shows):
        debut_year = show['release_year']
        show_name = show['tv_show_name']
        show_color = colors[i % len(colors)]
        show_name_to_color[show_name] = show_color
        for character in show['characters']:
            first_name = character.split()[0]
            debut_count = get_name_counts(first_name, name_data, debut_year)[0]
            percentage_jump = get_percentage_jump(first_name, name_data, debut_year)
            debut_popularities.append(debut_count)
            percentage_jumps.append(percentage_jump)
            name_labels.append(first_name)
            show_colors.append(show_color)
    debut_popularities = np.array(debut_popularities)
    percentage_jumps = np.array(percentage_jumps)
    name_labels = np.array(name_labels)
    show_colors = np.array(show_colors)
    mask = (debut_popularities > 0) & (percentage_jumps != 0)
    debut_popularities = debut_popularities[mask]
    percentage_jumps = percentage_jumps[mask]
    name_labels = name_labels[mask]
    show_colors = show_colors[mask]
    if len(debut_popularities) < 2:
        print("Not enough data points after filtering to perform regression.")
        return
    plt.figure(figsize=(12, 8))
    unique_colors = np.unique(show_colors)
    for color in unique_colors:
        plt.scatter(debut_popularities[show_colors == color], percentage_jumps[show_colors == color], color=color, alpha=0.7)
    m, b = np.polyfit(debut_popularities, percentage_jumps, 1)
    y_pred = m * debut_popularities + b
    ss_res = np.sum((percentage_jumps - y_pred) ** 2)
    ss_tot = np.sum((percentage_jumps - np.mean(percentage_jumps)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    pearson_corr = np.corrcoef(debut_popularities, percentage_jumps)[0, 1]
    x_range = np.linspace(min(debut_popularities), max(debut_popularities), 500)
    y_regression = m * x_range + b
    plt.plot(x_range, y_regression, color='black', label=f'Linear Regression: y = {m:.5f}x + {b:.2f}, $R^2$ = {r_squared:.2f}', linewidth=2)
    for i, name in enumerate(name_labels):
        plt.annotate(name, (debut_popularities[i], percentage_jumps[i]), fontsize=8, alpha=0.75)
    plt.title('Scatter Plot: Debut Popularity vs Percentage Jump in Popularity (7 Years After Debut)')
    plt.xscale('log')
    plt.xlabel('Debut Popularity (Number of Babies in Debut Year)')
    plt.ylabel('Percentage Jump in Popularity (7 Years)')
    handles = []
    labels = []
    for show_name, color in show_name_to_color.items():
        metrics = show_metrics.get(show_name, {})
        total_percentage_change = metrics.get('Total Percentage Change')
        if total_percentage_change is not None:
            total_pct_change_str = f" ({total_percentage_change:.1f}%)"
        else:
            total_pct_change_str = ""
        handle = plt.Line2D([0], [0], color=color, lw=2)
        label = f"{show_name}{total_pct_change_str}"
        handles.append(handle)
        labels.append(label)
    plt.legend(handles, labels, ncol=2, title=f'Regression: y = {m:.5f}x + {b:.2f}\nPearson Correlation: {pearson_corr:.2f}\n$R^2$: {r_squared:.2f}')
    plt.grid(True)
    plt.tight_layout()
    plt.text(0.99, 0.01, f"File: {os.path.basename(__file__)}", transform=plt.gca().transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right')
    plt.show()

folder_path = r'C:\Users\ybars\OneDrive - huji.ac.il\HUJI Documents Shana BET\MATAR Bet\Data Mining 47717\babynames text files'
name_data = load_name_data(folder_path)

def load_shows_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

shows_file_path = r'C:\Users\ybars\PycharmProjects\datamining\DM_Names_new_approach\output\tv_shows_new_release.json'
all_shows = load_shows_from_file(shows_file_path)

show_metrics = calculate_show_metrics(all_shows, name_data)
scatter_plot_linear_regression(all_shows, name_data, show_metrics)

for show_name, metrics in show_metrics.items():
    print(f"Show: {show_name}")
    print(f"  Average Percentage Jump: {metrics['Average Percentage Jump']}")
    print(f"  Total Percentage Change: {metrics['Total Percentage Change']}")
    print(f"  Weighted Average Percentage Jump: {metrics['Weighted Average Percentage Jump']}")
    print(f"  Number of Names Analyzed: {metrics['Number of Names']}\n")

def calculate_overall_metrics(all_shows, name_data):
    total_debut_count = 0
    total_avg_count_after = 0
    weighted_sum = 0
    for show in all_shows:
        debut_year = show['release_year']
        for character in show['characters']:
            first_name = character.split()[0]
            debut_count = get_name_counts(first_name, name_data, debut_year)[0]
            counts_after_debut = get_name_counts(first_name, data=name_data, start_year=debut_year)[1:8]
            avg_count_after_debut = sum(counts_after_debut) / len(counts_after_debut) if counts_after_debut else 0
            percentage_jump = get_percentage_jump(first_name, name_data, debut_year)
            if debut_count > 0:
                total_debut_count += debut_count
                total_avg_count_after += avg_count_after_debut
                weighted_sum += percentage_jump * debut_count
