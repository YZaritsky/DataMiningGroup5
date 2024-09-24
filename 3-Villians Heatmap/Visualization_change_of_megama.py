import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt

# Step 1: Load the CSV data from the file
df = pd.read_csv('output/top_10_box_office_movies_1977_2023_with_villains_origins.csv')

# Step 2: Define regions and exclude USA villains
regions = {
    'Islamic Countries': ['Iran', 'Iraq', 'Afghanistan', 'Syria', 'Pakistan', 'Saudi Arabia', 'Egypt', 'Turkey',
                          'Libya', 'Islamic'],
    'Communist Asia': ['China', 'North Korea'],
    'Russian/Ukrainian': ['Russia', 'USSR', 'Soviet Union', 'Ukraine', 'Stalingrad', 'Moscow', 'Kyiv']
}

# Filter out villains from the USA
df['Region'] = df['Origin'].apply(lambda x: next((region for region, places in regions.items() if x in places), 'Other'))
df = df[df['Region'] != 'USA']

# Step 3: Mark whether the country was in conflict with the USA
geopolitical_conflicts = {
    '1979-1981': {'event': 'Iran Hostage Crisis', 'region': 'Islamic Countries'},
    '1991-1993': {'event': 'Gulf War', 'region': 'Islamic Countries'},
    '2001-2001': {'event': '9/11', 'region': 'Islamic Countries'},
    '2002-2015': {'event': 'Iraq and Afghanistan Wars', 'region': 'Islamic Countries'},
    '2006-2018': {'event': 'North Korea Nuclear Threat', 'region': 'Communist Asia'},
    '2020-2024': {'event': 'China Marked as Greatest Threat to the USA', 'region': 'Communist Asia'},
    '1980-1985': {'event': 'Cold War Tension', 'region': 'Russian/Ukrainian'},
    '2014-2016': {'event': 'Ukraine Crisis', 'region': 'Russian/Ukrainian'},
    '2022-2024': {'event': 'Russia-Ukraine Conflict', 'region': 'Russian/Ukrainian'}
}

def get_conflict_status(year, region):
    for period, details in geopolitical_conflicts.items():
        start_year, end_year = period.split('-')
        if int(start_year) <= year <= (int(end_year) if end_year != 'present' else 9999):
            if details['region'] == region:
                return 1
    return 0

df['Conflict'] = df.apply(lambda row: get_conflict_status(row['Year'], row['Region']), axis=1)

# Step 4: Prepare the data for training
X = df[['Year', 'Conflict']]
y = df['Conflict']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Step 5: Train the Random Forest model
model = RandomForestClassifier(random_state=42, n_estimators=100)
model.fit(X_train, y_train)

# Step 6: Predict probabilities for each 5-year range from 1977 to 2030
years = list(range(1977, 2031, 5))
probabilities = []

for year in years:
    year_data = pd.DataFrame({
        'Year': [year],
        'Conflict': [1]  # Assume conflict
    })
    prob = model.predict_proba(year_data)[0][1]  # Probability of being in conflict
    probabilities.append(prob)

# Step 7: Visualize the probabilities
plt.figure(figsize=(12, 6))
plt.plot(years, [p * 100 for p in probabilities], marker='o')
plt.xlabel('Year')
plt.ylabel('Probability (%)')
plt.title('Probability that a Villain is from a Country in Conflict with the USA')
plt.grid(True)
plt.show()
