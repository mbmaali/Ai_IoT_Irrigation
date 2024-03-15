import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import joblib
from sklearn.metrics import accuracy_score

#Read Data
data = pd.read_excel('farm_dataset.xlsx')

# Extract the first four columns as features and the fifth column as the target
X = data.iloc[:, :4]
y = data.iloc[:, 4]
# Split data into features and target variable
X = data.drop('Pump (on/off)', axis=1)
y = data['Pump (on/off)']
# Training 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = DecisionTreeClassifier(random_state=42)
clf.fit(X_train, y_train)
#Test
y_pred = clf.predict(X_test)
#SAVING THE MODEL TO FILE
import joblib

# save the model to a file
filename = 'decision_tree_model.sav'
joblib.dump(clf, filename)
