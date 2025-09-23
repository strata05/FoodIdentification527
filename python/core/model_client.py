import os, threading
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from PIL import Image
from utils.file import UPLOAD_ROOT
from utils.s3_utils import get_s3_image
import io

ENV = os.getenv("ENV", "development")
MODEL_PATH = os.getenv("FOOD_MODEL_PATH", "models/best_model_101class.hdf5")
print(MODEL_PATH)
INPUT_SIZE = 200  # image size 200*200
DEFAULT_TOPK = 3

# 101 food category names
LABELS = [
    "apple pie",
    "baby back ribs",
    "baklava",
    "beef carpaccio",
    "beef tartare",
    "beet salad",
    "beignets",
    "bibimbap",
    "bread pudding",
    "breakfast burrito",
    "bruschetta",
    "caesar salad",
    "cannoli",
    "caprese salad",
    "carrot cake",
    "ceviche",
    "cheese plate",
    "cheesecake",
    "chicken curry",
    "chicken quesadilla",
    "chicken wings",
    "chocolate cake",
    "chocolate mousse",
    "churros",
    "clam chowder",
    "club sandwich",
    "crab cakes",
    "creme brulee",
    "croque madame",
    "cup cakes",
    "deviled eggs",
    "donuts",
    "dumplings",
    "edamame",
    "eggs benedict",
    "escargots",
    "falafel",
    "filet mignon",
    "fish and_chips",
    "foie gras",
    "french fries",
    "french onion soup",
    "french toast",
    "fried calamari",
    "fried rice",
    "frozen yogurt",
    "garlic bread",
    "gnocchi",
    "greek salad",
    "grilled cheese sandwich",
    "grilled salmon",
    "guacamole",
    "gyoza",
    "hamburger",
    "hot and sour soup",
    "hot dog",
    "huevos rancheros",
    "hummus",
    "ice cream",
    "lasagna",
    "lobster bisque",
    "lobster roll sandwich",
    "macaroni and cheese",
    "macarons",
    "miso soup",
    "mussels",
    "nachos",
    "omelette",
    "onion rings",
    "oysters",
    "pad thai",
    "paella",
    "pancakes",
    "panna cotta",
    "peking duck",
    "pho",
    "pizza",
    "pork chop",
    "poutine",
    "prime rib",
    "pulled pork sandwich",
    "ramen",
    "ravioli",
    "red velvet cake",
    "risotto",
    "samosa",
    "sashimi",
    "scallops",
    "seaweed salad",
    "shrimp and grits",
    "spaghetti bolognese",
    "spaghetti carbonara",
    "spring rolls",
    "steak",
    "strawberry shortcake",
    "sushi",
    "tacos",
    "octopus balls",
    "tiramisu",
    "tuna tartare",
    "waffles",
]

_model = None
_lock = threading.Lock()


def _load_model():
    """Load Keras model once"""
    global _model
    if _model is not None:
        return _model
    with _lock:
        if _model is None:
            from keras.models import load_model

            _model = load_model(MODEL_PATH, compile=False)
    return _model


def _preprocess(p: str) -> np.ndarray:
    image = None
    if ENV == "production":
        img_bytes = get_s3_image(p)
        image = Image.open(io.BytesIO(img_bytes))
    else:
        image = Image.open(UPLOAD_ROOT / p)

    image = image.convert("RGB").resize((INPUT_SIZE, INPUT_SIZE))
    return np.asarray(image, dtype=np.float32) / 255.0


def _postprocess(vec: np.ndarray, topk: int) -> List[Dict[str, Any]]:
    idx = np.argsort(vec)[::-1][:topk]  # take the first K from largest to smallest
    return [{"class": LABELS[i], "index": int(i), "score": float(vec[i])} for i in idx]


async def analyze_images(
    file_paths: List[str], topk: int = DEFAULT_TOPK
) -> Dict[str, Any]:
    """
    Return format:
    {
      "mock": False,
      "results": [
        {"file": "...", "topk": [{"class": "...", "index": 0, "score": 0.9}, ...]},
        ...
      ]
    }
    """
    model = _load_model()
    batch = np.stack([_preprocess(p) for p in file_paths], axis=0)
    preds = model.predict(batch, verbose=0)

    out = []
    for p, pred in zip(file_paths, preds):
        top = _postprocess(pred, topk)
        out.append({"file": p, "topk": top})

    return {"mock": False, "results": out}
