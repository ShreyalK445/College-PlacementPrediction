import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'College_placement.csv')
model_path = os.path.join(base_dir, 'model.pkl')

print("Loading data from:", csv_path)
df = pd.read_csv(csv_path)

# Drop index/unnamed column if it exists
if df.columns[0] == '' or df.columns[0].startswith('Unnamed'):
    df = df.iloc[:, 1:]

# Split features and target
X = df.drop(columns=['Placement'])
y = df['Placement']

print(f"Features: {list(X.columns)}")
print(f"Dataset size: {df.shape[0]} rows, {df.shape[1]} columns")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
print("Training RandomForestClassifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Validation Accuracy: {acc:.4f}")
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save model
print("Saving model to:", model_path)
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print("Model building complete!")
