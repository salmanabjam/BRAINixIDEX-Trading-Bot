"""
ML Model Compatibility Layer
=============================
Makes new improved ML model compatible with existing bot code.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class MLModelWrapper:
    """
    Wrapper to make new model compatible with old ml_engine.py
    """
    
    def __init__(self, model_path='models/trained_model.pkl', 
                 scaler_path='models/scaler.pkl',
                 features_path='models/feature_columns.pkl'):
        """Load the improved model"""
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            with open(features_path, 'rb') as f:
                self.feature_columns = pickle.load(f)
            
            print(f"✅ Model loaded: {len(self.feature_columns)} features")
            
        except FileNotFoundError as e:
            print(f"⚠️ Model files not found: {e}")
            self.model = None
            self.scaler = None
            self.feature_columns = None
    
    def predict(self, X_scaled):
        """
        Predict using the loaded model
        
        Args:
            X_scaled: Scaled feature array
            
        Returns:
            Array with shape (n_samples, 3) - probabilities for each class
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Get predictions
        y_pred = self.model.predict(X_scaled)
        y_proba = self.model.predict_proba(X_scaled)
        
        return y_proba
    
    def get_params(self, deep=True):
        """Compatibility method for sklearn"""
        return {}
    
    def set_params(self, **params):
        """Compatibility method for sklearn"""
        return self


def convert_model_format():
    """
    Convert the new improved model to be compatible with ml_engine.py
    """
    print("=" * 70)
    print("🔄 Converting ML Model Format")
    print("=" * 70)
    
    try:
        # Load new model
        print("\n📥 Loading improved model...")
        wrapper = MLModelWrapper()
        
        if wrapper.model is None:
            print("❌ Model not found. Please run train_improved_ml.py first.")
            return False
        
        # Test the wrapper
        print("\n🧪 Testing model wrapper...")
        
        # Create dummy data
        n_features = len(wrapper.feature_columns)
        X_test = np.random.randn(10, n_features)
        X_scaled = wrapper.scaler.transform(X_test)
        
        # Test prediction
        predictions = wrapper.predict(X_scaled)
        print(f"   Shape: {predictions.shape}")
        print(f"   Sample: {predictions[0]}")
        
        # Save wrapper
        print("\n💾 Saving wrapped model...")
        with open('models/trained_model_wrapped.pkl', 'wb') as f:
            pickle.dump(wrapper, f)
        
        print("✅ Model conversion complete!")
        print(f"   Saved to: models/trained_model_wrapped.pkl")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    convert_model_format()
