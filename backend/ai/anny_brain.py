import numpy as np
import json
import pickle
import nltk
from nltk.stem.lancaster import LancasterStemmer

# Initialize stemmer
stemmer = LancasterStemmer()

class AnnyBrain:
    """
    Custom Neural Network for Intent Classification
    Built from scratch using NumPy (No heavy frameworks like TensorFlow/PyTorch)
    """

    def __init__(self, input_nodes=0, hidden_nodes=8, output_nodes=0):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        
        # Initialize weights with random values
        if input_nodes > 0:
            self.weights_input_hidden = np.random.uniform(-1, 1, (input_nodes, hidden_nodes))
            self.weights_hidden_output = np.random.uniform(-1, 1, (hidden_nodes, output_nodes))
        
        self.words = []
        self.classes = []
        self.is_trained = False

    def sigmoid(self, x):
        """Activation function"""
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        """Derivative for backpropagation"""
        return x * (1 - x)

    def train(self, training_data_file='backend/ai/data/intents.json', epochs=3000):
        """Train the neural network on intent data"""
        print("Training ANNY Brain...")
        
        # Load dataset
        with open(training_data_file) as f:
            data = json.load(f)

        documents = []
        ignore_words = ['?', '!']
        
        # Preprocess data
        for intent in data['intents']:
            for pattern in intent['patterns']:
                # Tokenize
                w = nltk.word_tokenize(pattern)
                self.words.extend(w)
                documents.append((w, intent['tag']))
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        # Stem and sort
        self.words = [stemmer.stem(w.lower()) for w in self.words if w not in ignore_words]
        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

        print(f"Stats: {len(documents)} docs, {len(self.classes)} classes, {len(self.words)} unique words")

        # Create training data
        training = []
        output = []
        output_empty = [0] * len(self.classes)

        for doc in documents:
            bag = []
            pattern_words = doc[0]
            pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
            
            for w in self.words:
                bag.append(1) if w in pattern_words else bag.append(0)

            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1

            training.append(bag)
            output.append(output_row)

        training = np.array(training)
        output = np.array(output)

        # Setup Network Architecture
        self.input_nodes = len(training[0])
        self.output_nodes = len(output[0])
        self.hidden_nodes = 32 # Increased for complex intents
        
        self.weights_input_hidden = 2 * np.random.random((self.input_nodes, self.hidden_nodes)) - 1
        self.weights_hidden_output = 2 * np.random.random((self.hidden_nodes, self.output_nodes)) - 1

        # Training Loop (Backpropagation)
        for i in range(epochs):
            # Feed Forward
            input_layer = training
            hidden_layer = self.sigmoid(np.dot(input_layer, self.weights_input_hidden))
            output_layer = self.sigmoid(np.dot(hidden_layer, self.weights_hidden_output))

            # Calculate Error
            output_error = output - output_layer
            
            if (i % 100) == 0:
                print(f"Epoch {i} Error: {np.mean(np.abs(output_error))}")

            # Backpropagation
            output_delta = output_error * self.sigmoid_derivative(output_layer)
            hidden_error = output_delta.dot(self.weights_hidden_output.T)
            hidden_delta = hidden_error * self.sigmoid_derivative(hidden_layer)

            # Update Weights (with learning rate)
            lr = 0.1
            self.weights_hidden_output += hidden_layer.T.dot(output_delta) * lr
            self.weights_input_hidden += input_layer.T.dot(hidden_delta) * lr

        self.is_trained = True
        self.save_brain()
        print("Training Complete!")

    def predict(self, sentence):
        """Predict intent of a sentence"""
        if not self.is_trained:
            return "Brain not trained"

        # Bag of words
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
        bag = [0]*len(self.words)
        for s in sentence_words:
            for i, w in enumerate(self.words):
                if w == s:
                    bag[i] = 1

        # Feed forward
        input_layer = np.array([bag])
        hidden_layer = self.sigmoid(np.dot(input_layer, self.weights_input_hidden))
        output_layer = self.sigmoid(np.dot(hidden_layer, self.weights_hidden_output))
        
        results = output_layer[0]
        results_index = np.argmax(results)
        
        tag = self.classes[results_index]
        confidence = results[results_index]
        
        return tag, confidence

    def save_brain(self, filename='backend/ai/data/brain_weights.pkl'):
        """Save specialized internal format"""
        data = {
            'w1': self.weights_input_hidden,
            'w2': self.weights_hidden_output,
            'words': self.words,
            'classes': self.classes
        }
        with open(filename, "wb") as f:
            pickle.dump(data, f)

    def load_brain(self, filename='backend/ai/data/brain_weights.pkl'):
        """Load trained brain"""
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
                self.weights_input_hidden = data['w1']
                self.weights_hidden_output = data['w2']
                self.words = data['words']
                self.classes = data['classes']
                self.is_trained = True
                return True
        except:
            return False

if __name__ == "__main__":
    # Train the brain
    brain = AnnyBrain()
    brain.train()
    
    # Test
    print(brain.predict("Lock my computer"))
    print(brain.predict("please and thank you")) 
