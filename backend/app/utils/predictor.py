"""PyTorch inference service for PomeXAI FusionNet."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from app.config import DISEASE_CLASSES, DISPLAY_NAMES, get_settings
from app.models.fusion_net import PomeXAIFusionNet
from app.recommendation.engine import build_diagnosis_payload

logger = logging.getLogger(__name__)
settings = get_settings()

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def clean_state_dict(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {}
    for key, value in state_dict.items():
        if key.startswith("module."):
            key = key[7:]
        cleaned[key] = value
    return cleaned


class PredictorService:
    """Loads the trained FusionNet checkpoint and runs image inference."""

    def __init__(self) -> None:
        self.model: Optional[torch.nn.Module] = None
        self.class_names: List[str] = list(DISEASE_CLASSES)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._loaded_path: Optional[str] = None
        self.img_size = settings.img_size
        self.best_val_accuracy: Optional[float] = None
        self.model_name: str = "PomeXAI_FusionNet"
        self.transform = transforms.Compose(
            [
                transforms.Resize((self.img_size, self.img_size)),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            ]
        )

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def load(self, model_path: Optional[str] = None) -> None:
        path = model_path or settings.resolved_model_path
        if self.model is not None and self._loaded_path == path:
            return

        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(
                f"Trained model not found at {path}. "
                "Place PomeXAI_FusionNet_best.pt in the models/ folder."
            )

        logger.info("Loading checkpoint from %s on %s", path, self.device)
        ckpt = torch.load(path_obj, map_location=self.device, weights_only=False)

        if not isinstance(ckpt, dict):
            raise ValueError(f"Unsupported checkpoint format in {path_obj.name}")

        classes = ckpt.get("classes") or ckpt.get("class_names")
        if not classes and ckpt.get("class_to_idx"):
            classes = [
                name
                for name, _ in sorted(ckpt["class_to_idx"].items(), key=lambda kv: kv[1])
            ]
        if classes:
            self.class_names = list(classes)

        self.img_size = int(ckpt.get("img_size") or settings.img_size)
        self.best_val_accuracy = ckpt.get("best_val_accuracy")
        self.model_name = ckpt.get("model_name") or ckpt.get("architecture") or "PomeXAI_FusionNet"

        self.transform = transforms.Compose(
            [
                transforms.Resize((self.img_size, self.img_size)),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            ]
        )

        state = (
            ckpt.get("model_state")
            or ckpt.get("state_dict")
            or ckpt.get("model")
        )
        if state is None:
            raise KeyError(
                f"No model_state/state_dict found in {path_obj.name}. Keys: {list(ckpt.keys())}"
            )

        model = PomeXAIFusionNet(num_classes=len(self.class_names))
        missing, unexpected = model.load_state_dict(clean_state_dict(state), strict=False)
        if missing:
            logger.warning("Missing keys while loading: %s", len(missing))
        if unexpected:
            logger.warning("Unexpected keys while loading: %s", len(unexpected))

        model.to(self.device)
        model.eval()
        self.model = model
        self._loaded_path = path
        logger.info(
            "Loaded %s | classes=%s | img_size=%s | val_acc=%s",
            self.model_name,
            self.class_names,
            self.img_size,
            self.best_val_accuracy,
        )

    def _preprocess(self, image: Image.Image) -> torch.Tensor:
        rgb = image.convert("RGB")
        tensor = self.transform(rgb).unsqueeze(0)
        return tensor.to(self.device)

    def predict_from_image(self, image: Image.Image) -> Dict[str, Any]:
        self.load()
        assert self.model is not None

        batch = self._preprocess(image)
        with torch.no_grad():
            logits = self.model(batch)
            probabilities = F.softmax(logits, dim=1)[0].cpu().numpy()

        class_index = int(probabilities.argmax())
        confidence = float(probabilities[class_index])
        disease_name = self.class_names[class_index]
        display_name = DISPLAY_NAMES.get(disease_name, disease_name.replace("_", " "))

        diagnosis = build_diagnosis_payload(disease_name, confidence)
        diagnosis["disease_name"] = disease_name
        diagnosis["display_name"] = display_name
        diagnosis["probabilities"] = {
            self.class_names[i]: round(float(probabilities[i]) * 100, 2)
            for i in range(len(self.class_names))
        }
        diagnosis["model_name"] = self.model_name
        diagnosis["device"] = str(self.device)
        diagnosis["explainability"] = {
            "method": "Softmax confidence from PomeXAI FusionNet",
            "predicted_class_index": class_index,
        }
        return diagnosis

    def predict_from_path(self, image_path: str) -> Dict[str, Any]:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Cannot read image: {image_path}")
        try:
            with Image.open(path) as img:
                return self.predict_from_image(img)
        except Exception as exc:
            raise ValueError(f"Invalid or unreadable image: {exc}") from exc

    def model_info(self) -> Dict[str, Any]:
        try:
            self.load()
            loaded = True
            error = None
        except Exception as exc:
            loaded = False
            error = str(exc)

        return {
            "loaded": loaded,
            "model_name": self.model_name,
            "model_path": self._loaded_path or settings.resolved_model_path,
            "classes": self.class_names,
            "img_size": self.img_size,
            "device": str(self.device),
            "best_val_accuracy": self.best_val_accuracy,
            "error": error,
        }


predictor = PredictorService()
