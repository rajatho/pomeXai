# Research Methodology

## Problem Statement

Automated detection of pomegranate diseases from leaf/fruit images to enable timely intervention and optimized fertilizer use.

## Proposed Method

1. **Data Collection & Preprocessing** — Curated image dataset with augmentation and balancing.
2. **Baseline CNN** — Custom Keras CNN with Conv-BatchNorm-ReLU-Pool-Dropout blocks.
3. **WOA Optimization** — Meta-heuristic search over hyperparameter space to maximize validation accuracy and minimize validation loss.
4. **Explainability** — Grad-CAM heatmaps for interpretable predictions.
5. **Recommendation Engine** — Rule-based agronomic knowledge base mapping diseases to fertilizers and treatments.
6. **Deployment** — FastAPI backend + React frontend for field use.

## Evaluation Metrics

- Accuracy, Precision, Recall, F1 Score
- Specificity, Sensitivity
- ROC-AUC (one-vs-rest)
- Confusion Matrix
- Training time comparison: CNN vs CNN+WOA

## WOA Formulation

Fitness = `-val_accuracy + 0.5 * val_loss` (minimize)

Search space includes learning rate, batch size, convolution filters, kernel size, dropout, dense units, epoch count, optimizer, and activation function.

## References

- Mirjalili, S., & Lewis, A. (2016). The Whale Optimization Algorithm. *Advances in Engineering Software*.
- Selvaraju et al. (2017). Grad-CAM: Visual Explanations from Deep Networks.
