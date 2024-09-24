import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt

# Step 1: Load the CSV data
df = pd.read_csv('output/top_10_box_office_movies_1977_2023_with_villains_origins.csv')

# Define the list of UN member states (excluding the USA)
un_countries = ['Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 
                'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 
                'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 
                'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 
                'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 
                'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 
                'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 
                'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 
                'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 
                'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 
                'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 
                'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 
                'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 
                'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 
                'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 
                'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 
                'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 
                'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 
                'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 
                'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 
                'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 
                'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 
                'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 
                'United Kingdom', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 
                'Zimbabwe']

# Step 2: Standardize country names and remove US-origin villains
def standardize_origin(origin):
    if pd.isna(origin):
        return np.nan
    origin = origin.strip()
    if 'Hong Kong' in origin:
        return 'China'
    if 'England' in origin:
        return 'United Kingdom'
    return origin

df['Standardized_Origin'] = df['Origin'].apply(standardize_origin)

# Remove villains from USA and filter only UN countries
usa_variants = ['USA', 'United States', 'Haddonfield, Illinois', '112 Ocean Avenue, Amityville, New York', 
                'Los Angeles, USA', 'New York, USA', 'Chicago, USA']
df = df[~df['Standardized_Origin'].isin(usa_variants)]
df = df[df['Standardized_Origin'].isin(un_countries)]
df = df[df['Standardized_Origin'].notna()]

# Define regions and conflicts
regions = {
    'Islamic Countries': ['Iran', 'Iraq', 'Afghanistan', 'Syria', 'Pakistan', 'Saudi Arabia', 'Egypt', 'Turkey', 'Libya', 'Islamic'],
    'Communist Asia': ['China', 'North Korea'],
    'Russian/Ukrainian': ['Russia', 'USSR', 'Soviet Union', 'Ukraine', 'Stalingrad', 'Moscow', 'Kyiv']
}

# Geopolitical conflicts data (year ranges for conflicts)
geopolitical_conflicts = {
    'Islamic Countries': [(1979, 1981), (1991, 1993), (2001, 2001), (2002, 2015)],  # Iran Hostage Crisis, Gulf War, 9/11, Iraq/Afghanistan wars
    'Communist Asia': [(2006, 2018), (2020, 2024)],  # North Korea nuclear threat, China-US tensions
    'Russian/Ukrainian': [(1980, 1985), (2014, 2016), (2022, 2024)]  # Cold War, Ukraine crisis
}

# Step 3: Helper function to determine if a country is in conflict and calculate decay effect
def is_in_conflict_and_decay(origin, year):
    decay_factor = 0
    in_conflict = 0
    for region, countries in regions.items():
        if origin in countries:
            for conflict_start, conflict_end in geopolitical_conflicts[region]:
                if conflict_start <= year <= conflict_end:
                    in_conflict = 1  # In conflict
                elif year > conflict_end:
                    # Calculate decay effect for years after conflict
                    years_after_conflict = year - conflict_end
                    decay_factor += np.exp(-years_after_conflict)  # Exponential decay
    return in_conflict, decay_factor

df['In_Conflict'], df['Decay_Effect'] = zip(*df.apply(lambda row: is_in_conflict_and_decay(row['Standardized_Origin'], row['Year']), axis=1))

# Step 4: Feature engineering and splitting data
X = df[['Year', 'Decay_Effect']]
y = df['In_Conflict']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 5: Use SMOTE to handle class imbalance
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

# Step 6: Train a Random Forest Classifier
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train_smote, y_train_smote)

# Step 7: Make predictions on the test set
y_pred = clf.predict(X_test)
y_pred_proba = clf.predict_proba(X_test)[:, 1]  # Get probabilities for the positive class

# Step 8: Evaluate the model
conf_matrix = confusion_matrix(y_test, y_pred)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=1)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print("Confusion Matrix:\n", conf_matrix)
print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1 Score: {f1:.2f}")
print(f"ROC AUC Score: {roc_auc:.2f}")

# Step 9: Plot the ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

plt.figure()
plt.plot(fpr, tpr, color='blue', label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='red', linestyle='--')  # Random guessing line
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

# Step 10: Predict for Sweden in 2025 when not in conflict
# Create a DataFrame for 2025 with no conflict (Decay_Effect = 0) for Sweden
df_sweden_not_in_conflict = pd.DataFrame({'Year': [2025], 'Decay_Effect': [0]})

# Predict the probability of a villain being from Sweden in 2025 when not in conflict
probability_not_in_conflict = clf.predict_proba(df_sweden_not_in_conflict)[:, 1]
print(f"Probability of a villain being from Sweden in 2025 when not in conflict: {probability_not_in_conflict[0]:.4f}")

# Step 11: Predict for Sweden in 2025 when in conflict
# Create a DataFrame for 2025 and flag Sweden as being in conflict
df_sweden_in_conflict = pd.DataFrame({'Year': [2025], 'Decay_Effect': [1]})  # Setting decay effect high for active conflict

# Predict the probability of a villain being from Sweden in 2025 when in conflict
probability_in_conflict = clf.predict_proba(df_sweden_in_conflict)[:, 1]
print(f"Probability of a villain being from Sweden in 2025 when in conflict: {probability_in_conflict[0]:.4f}")
