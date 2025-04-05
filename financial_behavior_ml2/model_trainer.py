from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
import os

class ModelTrainer:
    def __init__(self):
        self.model = None
        
    def create_model(self):
        """Create a Random Forest model for savings prediction"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        return model
    
    def train_model(self, X_train, y_train, X_val, y_val):
        """Train the model on the provided data"""
        # Create and train model
        self.model = self.create_model()
        self.model.fit(X_train, y_train)
        
        # Calculate training accuracy
        train_accuracy = self.model.score(X_train, y_train)
        val_accuracy = self.model.score(X_val, y_val)
        
        return {
            'train_accuracy': train_accuracy,
            'val_accuracy': val_accuracy
        }
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate the model on test data"""
        y_pred = self.model.predict(X_test)
        
        return classification_report(y_test, y_pred, 
                                  target_names=['Below Target', 'Above Target'])
    
    def save_model(self, model_path='models'):
        """Save the trained model"""
        if not os.path.exists(model_path):
            os.makedirs(model_path)
            
        joblib.dump(self.model, os.path.join(model_path, 'savings_classifier.joblib'))
    
    def load_model(self, model_path='models'):
        """Load a saved model"""
        self.model = joblib.load(os.path.join(model_path, 'savings_classifier.joblib')) 