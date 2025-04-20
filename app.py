from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models and vocabs
models = {}
vocabs = {}

for model_type in ['cap', 'word', 'num', 'special']:
    models[model_type] = tf.keras.models.load_model(f"model_artifacts/{model_type}_model.h5")
    with open(f"model_artifacts/{model_type}_vocab.pkl", "rb") as f:
        c2i, i2c, max_len = pickle.load(f)
        vocabs[model_type] = {
            'char_to_index': c2i,
            'index_to_char': i2c,
            'max_length': max_len
        }

def generate_password(model, vocab, seed, length=10, temperature=1.0):
    """Generate password using the model"""
    generated = []
    current_seq = [vocab['char_to_index'][c] for c in seed]
    
    for _ in range(length):
        padded_seq = pad_sequences([current_seq], maxlen=vocab['max_length'], padding='pre')
        preds = model.predict(padded_seq, verbose=0)[0]
        
        # Apply temperature
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        
        next_index = np.random.choice(len(preds), p=preds)
        next_char = vocab['index_to_char'].get(next_index, '')
        
        if not next_char:
            break
            
        generated.append(next_char)
        current_seq.append(next_index)
        
    return seed + ''.join(generated)

@app.get("/generate-password")
async def generate(
    ptype: str = "word", 
    seed: str = "ab", 
    length: int = 10,
    temperature: float = 0.8
):
    """Generate password endpoint"""
    if ptype not in ['cap', 'word', 'num', 'special']:
        return {"error": "Invalid password type"}
    
    try:
        password = generate_password(
            models[ptype],
            vocabs[ptype],
            seed,
            length,
            temperature
        )
        return {
            "password": password,
            "type": ptype,
            "seed": seed,
            "length": len(password)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Password Generation API",
        "endpoints": {
            "/generate-password": {
                "params": {
                    "ptype": "password type (cap|word|num|special)",
                    "seed": "starting characters",
                    "length": "desired length",
                    "temperature": "creativity control (0.1-2.0)"
                }
            }
        }
    }