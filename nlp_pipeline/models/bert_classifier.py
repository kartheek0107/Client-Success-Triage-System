from transformers import pipeline
import os
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BERTTicketClassifier:
    def __init__(self):
        priority_path = "models/artifacts/bert-priority-model"
        category_path = "models/artifacts/bert-category-model"

        # Use top_k=None to ensure list output
        self.priority_classifier = pipeline(
            "text-classification",
            model=priority_path,
            tokenizer=priority_path,
            device=-1,
            top_k=None  # Always return list
        )

        self.category_classifier = pipeline(
            "text-classification",
            model=category_path,
            tokenizer=category_path,
            device=-1,
            top_k=None
        )

    def _extract_prediction(self, outputs, classifier_name):
        """Helper method to safely extract prediction from pipeline output."""
        logger.info(f"{classifier_name} raw output: {outputs}")
        logger.info(f"{classifier_name} output type: {type(outputs)}")
        
        try:
            # Handle nested list structure [[{...}]] -> [{...}]
            current = outputs
            while isinstance(current, list) and len(current) == 1 and isinstance(current[0], list):
                current = current[0]
                logger.info(f"{classifier_name} unwrapped nested list: {current}")
            
            # Case 1: List of predictions
            if isinstance(current, list):
                if len(current) == 0:
                    raise ValueError(f"{classifier_name} returned empty list")
                
                # Get the first (highest confidence) prediction
                prediction = current[0]
                logger.info(f"{classifier_name} first prediction: {prediction}")
                
                # Check if it's a dict with expected keys
                if isinstance(prediction, dict) and 'label' in prediction and 'score' in prediction:
                    return prediction
                else:
                    raise ValueError(f"{classifier_name} prediction format unexpected: {prediction}")
            
            # Case 2: Single dict (shouldn't happen with top_k=None, but let's handle it)
            elif isinstance(current, dict) and 'label' in current and 'score' in current:
                return current
            
            # Case 3: Unexpected format
            else:
                raise ValueError(f"{classifier_name} returned unexpected format: {type(current)} - {current}")
                
        except Exception as e:
            logger.error(f"Error extracting prediction from {classifier_name}: {str(e)}")
            raise

    def classify(self, subject: str, description: str) -> dict:
        text = f"{subject} {description}"
        logger.info(f"Classifying text: {text[:100]}...")  # Log first 100 chars

        try:
            # Classify priority
            priority_outputs = self.priority_classifier(text)
            priority = self._extract_prediction(priority_outputs, "priority_classifier")

            # Classify category
            category_outputs = self.category_classifier(text)
            category = self._extract_prediction(category_outputs, "category_classifier")

            result = {
                "priority": str(priority["label"]),
                "priority_confidence": round(float(priority["score"]), 4),
                "category": str(category["label"]),
                "category_confidence": round(float(category["score"]), 4)
            }
            
            logger.info(f"Classification result: {result}")
            return result

        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            raise RuntimeError(f"Failed to classify: {str(e)}")


# Alternative version with even more defensive programming
class BERTTicketClassifierRobust:
    def __init__(self):
        priority_path = "models/artifacts/bert-priority-model"
        category_path = "models/artifacts/bert-category-model"

        # Try different configurations
        try:
            # First try with top_k=None
            self.priority_classifier = pipeline(
                "text-classification",
                model=priority_path,
                tokenizer=priority_path,
                device=-1,
                top_k=None
            )
        except Exception as e:
            logger.warning(f"Failed to create priority classifier with top_k=None: {e}")
            # Fallback without top_k
            self.priority_classifier = pipeline(
                "text-classification",
                model=priority_path,
                tokenizer=priority_path,
                device=-1
            )

        try:
            self.category_classifier = pipeline(
                "text-classification",
                model=category_path,
                tokenizer=category_path,
                device=-1,
                top_k=None
            )
        except Exception as e:
            logger.warning(f"Failed to create category classifier with top_k=None: {e}")
            self.category_classifier = pipeline(
                "text-classification",
                model=category_path,
                tokenizer=category_path,
                device=-1
            )

    def _safe_extract_prediction(self, outputs, classifier_name):
        """Ultra-safe prediction extraction."""
        logger.info(f"{classifier_name} output: {outputs} (type: {type(outputs)})")
        
        # Handle nested lists (sometimes pipelines return [[{...}]])
        while isinstance(outputs, list) and len(outputs) == 1 and isinstance(outputs[0], list):
            outputs = outputs[0]
            logger.info(f"Unwrapped nested list: {outputs}")
        
        # Now handle the main cases
        if isinstance(outputs, list) and len(outputs) > 0:
            prediction = outputs[0]
            if isinstance(prediction, dict):
                return {
                    'label': str(prediction.get('label', 'UNKNOWN')),
                    'score': float(prediction.get('score', 0.0))
                }
        elif isinstance(outputs, dict):
            return {
                'label': str(outputs.get('label', 'UNKNOWN')),
                'score': float(outputs.get('score', 0.0))
            }
        
        # Fallback for unexpected formats
        logger.error(f"Unexpected output format from {classifier_name}: {outputs}")
        return {'label': 'ERROR', 'score': 0.0}

    def classify(self, subject: str, description: str) -> dict:
        text = f"{subject} {description}"
        
        try:
            # Get predictions with error handling
            priority_outputs = self.priority_classifier(text)
            priority = self._safe_extract_prediction(priority_outputs, "priority")
            
            category_outputs = self.category_classifier(text)
            category = self._safe_extract_prediction(category_outputs, "category")

            return {
                "priority": priority["label"],
                "priority_confidence": round(priority["score"], 4),
                "category": category["label"],
                "category_confidence": round(category["score"], 4)
            }

        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            # Return default values instead of failing
            return {
                "priority": "MEDIUM",
                "priority_confidence": 0.0,
                "category": "GENERAL",
                "category_confidence": 0.0,
                "error": str(e)
            }