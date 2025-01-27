import os
import random
from collections import defaultdict, Counter
from typing import Dict, List, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class NameGenerator:
    def __init__(self, rng: np.random.Generator, data_dir: str = "data/names"):
        self.rng = rng
        self.data_dir = data_dir
        self.markov_models: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.load_models()

    def load_models(self):
        """Load Markov models from data directory"""
        if not os.path.exists(self.data_dir):
            logger.warning(f"Name data directory not found: {self.data_dir}")
            return

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".txt"):
                model_name = filename[:-4]  # Remove .txt extension
                self.markov_models[model_name] = self._build_markov_model(
                    os.path.join(self.data_dir, filename)
                )

    def _build_markov_model(self, filepath: str, order: int = 2) -> Dict[str, Dict[str, float]]:
        """Build a Markov model from a text file of names"""
        model = defaultdict(Counter)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip().lower()
                if not name:
                    continue
                
                # Pad the name with start/end markers
                name = " " * order + name + " "
                
                for i in range(len(name) - order):
                    current = name[i:i+order]
                    next_char = name[i+order]
                    model[current][next_char] += 1

        # Convert counts to probabilities
        prob_model = {}
        for current, next_chars in model.items():
            total = sum(next_chars.values())
            prob_model[current] = {
                char: count / total for char, count in next_chars.items()
            }
            
        return prob_model

    def generate_name(self, 
                     epoch: str = "empire",
                     culture: Optional[str] = None,
                     name_type: str = "settlement",
                     min_length: int = 3,
                     max_length: int = 12) -> str:
        """Generate a name based on parameters"""
        # Determine which model to use
        model_key = f"{epoch}_{name_type}"
        if culture:
            model_key = f"{epoch}_{culture}_{name_type}"
            
        model = self.markov_models.get(model_key)
        if not model:
            logger.warning(f"No model found for {model_key}, using default")
            model = self.markov_models.get("default")
            if not model:
                raise ValueError("No default name model found")

        # Generate name using Markov chain
        order = len(next(iter(model.keys())))
        name = " " * order  # Start with padding
        
        while True:
            current = name[-order:]
            next_char = self._choose_next_char(model[current])
            name += next_char
            
            if next_char == " " and len(name.strip()) >= min_length:
                break
            if len(name.strip()) >= max_length:
                break

        return name.strip().title()

    def _choose_next_char(self, probabilities: Dict[str, float]) -> str:
        """Choose next character based on probabilities"""
        chars, weights = zip(*probabilities.items())
        return self.rng.choice(chars, p=weights)

# Example usage:
# generator = NameGenerator(np.random.default_rng())
# print(generator.generate_name(epoch="empire", name_type="settlement"))
# print(generator.generate_name(epoch="mythic", name_type="dungeon")) 