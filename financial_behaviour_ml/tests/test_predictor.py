import unittest
import pandas as pd
import joblib
from src.data_processor import DataProcessor
from src.behavior_predictor import BehaviorPredictor
from config import *

class TestBehaviorPredictor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.processor = DataProcessor()
        cls.X_train, cls.X_test, cls.y_train, cls.y_test = cls.processor.get_train_test()
        cls.predictor = BehaviorPredictor()
        cls.predictor.train_and_save(cls.X_train, cls.y_train)
    
    def test_model_loading(self):
        model = joblib.load(MODEL_PATH)
        self.assertIsNotNone(model)
    
    def test_prediction(self):
        test_user = {
            'income': 75000,
            'age': 32,
            'dependents': 1,
            'occupation': 'engineer',
            'city_tier': 1,
            'total_needs': 35000,
            'total_wants': 15000,
            'savings_ratio': 0.2,
            'disposable_ratio': 0.6
        }
        
        prediction = self.predictor.predict_behavior(test_user)
        self.assertIn(prediction, ['want-driven', 'need-driven'])

if __name__ == '__main__':
    unittest.main()