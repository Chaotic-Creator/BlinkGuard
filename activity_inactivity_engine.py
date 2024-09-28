import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from simulate_data import simulate_data

def train_model():
    # Simulate data
    usage_data, inactivity_data, activity_labels = simulate_data()

    # Combine data into a feature matrix
    X = np.column_stack((usage_data, inactivity_data))

    # Encode activity labels (convert labels to numeric values)
    label_map = {"break needed": 1, "no break needed": 0}
    y = np.array([label_map[label] for label in activity_labels])

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train a simple Random Forest classifier
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = clf.predict(X_test)

    # Evaluate the model's accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    return clf

model = train_model()

def predict(data):
    labels = ["no break needed", "break needed"]
    pred = model.predict([data])[0]
    return labels[pred]

# Should we embed this into ai_engine.py?
