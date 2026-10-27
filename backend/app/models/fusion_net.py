"""PomeXAI FusionNet architecture (ResNet50 + ViT with gated fusion)."""

from __future__ import annotations

import torch
import torch.nn as nn
import timm


class SpatialAttention(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        hidden = max(channels // 8, 16)
        self.net = nn.Sequential(
            nn.Linear(channels, hidden),
            nn.GELU(),
            nn.Linear(hidden, channels),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.net(x)


class PomeXAIFusionNet(nn.Module):
    """Hybrid CNN–ViT fusion network used by the trained checkpoint."""

    def __init__(self, num_classes: int) -> None:
        super().__init__()
        # pretrained=False: weights come from the saved checkpoint only.
        self.cnn = timm.create_model(
            "resnet50", pretrained=False, num_classes=0, global_pool="avg"
        )
        self.vit = timm.create_model(
            "vit_base_patch16_224", pretrained=False, num_classes=0
        )

        cnn_dim = self.cnn.num_features
        vit_dim = self.vit.num_features
        fusion_dim = 512

        self.cnn_proj = nn.Sequential(
            nn.Linear(cnn_dim, fusion_dim),
            nn.LayerNorm(fusion_dim),
            nn.GELU(),
        )
        self.vit_proj = nn.Sequential(
            nn.Linear(vit_dim, fusion_dim),
            nn.LayerNorm(fusion_dim),
            nn.GELU(),
        )
        self.gate = nn.Sequential(
            nn.Linear(fusion_dim * 2, fusion_dim),
            nn.GELU(),
            nn.Linear(fusion_dim, fusion_dim),
            nn.Sigmoid(),
        )
        self.spatial_attention = SpatialAttention(fusion_dim)
        self.dropout = nn.Dropout(0.35)
        self.head = nn.Sequential(
            nn.Linear(fusion_dim, 256),
            nn.GELU(),
            nn.Dropout(0.25),
            nn.Linear(256, num_classes),
        )

    def forward_features(self, x: torch.Tensor):
        cnn_f = self.cnn(x)
        vit_f = self.vit(x)
        a = self.cnn_proj(cnn_f)
        b = self.vit_proj(vit_f)
        g = self.gate(torch.cat([a, b], dim=1))
        fused = g * a + (1 - g) * b
        fused = self.spatial_attention(fused)
        return fused, cnn_f, vit_f, g

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        fused, _, _, _ = self.forward_features(x)
        return self.head(self.dropout(fused))
