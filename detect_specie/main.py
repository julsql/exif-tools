from pathlib import Path

import birder
from birder.inference.classification import infer_image
import requests

MODEL_PATH = Path.home() / ".exiftools" / "models" / "vit_reg4_m16_rms_avg_i-jepa-inat21.pt"

# Charger le modèle et les infos
net, model_info = birder.load_pretrained_model(
    "vit_reg4_m16_rms_avg_i-jepa-inat21",
    inference=True,
    dst=MODEL_PATH
)
class_mapping = {v: k for k, v in model_info.class_to_idx.items()}

# Créer la transformation
size = birder.get_size_from_signature(model_info.signature)
transform = birder.classification_transform(size, model_info.rgb_stats)


def get_latin_name(class_id):
    full_latin_name = class_mapping.get(class_id, "")
    return " ".join(full_latin_name.split("_")[-2:])


def is_species_at_location(scientific_name, lat, lon, radius_km=500):
    """
    Vérifie si l'espèce est observée près de la localisation donnée via l'API iNaturalist.
    """
    if not scientific_name or lat is None or lon is None:
        return False

    url = "https://api.inaturalist.org/v1/observations"
    params = {
        "taxon_name": scientific_name,
        "lat": lat,
        "lng": lon,
        "radius": radius_km,
        "per_page": 1
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_results", 0) > 0
    except Exception:
        return False


def find_specie(image_path, lat=None, lon=None, threshold=0.2):
    """
    Infère l'espèce de l'image et utilise la localisation pour valider la prédiction.
    Retourne le nom scientifique si trouvé, sinon "".
    """
    # inférence du modèle
    out, _ = infer_image(net, image_path, transform)
    probs = out[0]

    sorted_indices = probs.argsort()[::-1]

    for class_id in sorted_indices:
        score = probs[class_id]
        if score < threshold:
            continue

        scientific_name = get_latin_name(class_id)
        if lat is None or lon is None:
            return scientific_name
        if is_species_at_location(scientific_name, lat, lon):
            return scientific_name

    # aucun match avec la localisation
    return ""
