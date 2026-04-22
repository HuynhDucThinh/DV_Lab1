"""Train and explain a Tiki best-seller classifier.

This module implements the full ML workflow requested in MachineLearning.md:
1) Join fact_tiki + dim_product + dim_category
2) Feature engineering (Price_Gap, frequency encoding for category/brand)
3) Handle class imbalance with XGBoost scale_pos_weight
4) Evaluate with Confusion Matrix and ROC-AUC
5) Explain model with SHAP values
6) Export artifacts to models/
"""

from __future__ import annotations

from pathlib import Path
import json
import pickle

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import (
	confusion_matrix,
	roc_auc_score,
	roc_curve,
	classification_report,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import matplotlib.pyplot as plt


RANDOM_STATE = 42
TARGET_COL = "Is_Best_Seller"


def load_and_join_data(data_dir: Path) -> pd.DataFrame:
	"""Load and join fact + dimensions for Tiki products."""
	fact_path = data_dir / "fact_tiki_listings.csv"
	product_path = data_dir / "dim_product.csv"
	category_path = data_dir / "dim_category.csv"

	df_fact = pd.read_csv(fact_path, dtype={"product_id": str})
	df_product = pd.read_csv(product_path, dtype={"product_id": str, "category_id": str})
	df_category = pd.read_csv(category_path, dtype={"category_id": str})

	joined = df_fact.merge(
		df_product[["product_id", "brand", "category_id"]],
		on="product_id",
		how="left",
	)
	joined = joined.merge(
		df_category[["category_id", "category"]],
		on="category_id",
		how="left",
	)
	return joined


def preprocess_and_engineer_features(df: pd.DataFrame) -> pd.DataFrame:
	"""Clean raw columns and create engineered features."""
	out = df.copy()

	numeric_cols = [
		"price",
		"original_price",
		"discount_rate",
		"rating_average",
		TARGET_COL,
	]
	for col in numeric_cols:
		out[col] = pd.to_numeric(out[col], errors="coerce")

	out["brand"] = out["brand"].fillna("Unknown").astype(str)
	out["category"] = out["category"].fillna("Unknown").astype(str)

	out["Price_Gap"] = out["original_price"] - out["price"]
	out["Price_Gap"] = out["Price_Gap"].clip(lower=0)

	out = out.dropna(subset=numeric_cols)
	out[TARGET_COL] = out[TARGET_COL].astype(int)

	return out


def add_frequency_encoding(
	train_df: pd.DataFrame,
	test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, float]]]:
	"""Add frequency-encoded categorical features using train-only statistics."""
	train_out = train_df.copy()
	test_out = test_df.copy()

	encoders: dict[str, dict[str, float]] = {}
	for col in ["brand", "category"]:
		freq = train_out[col].value_counts(normalize=True).to_dict()
		encoders[col] = freq

		train_out[f"{col}_freq"] = train_out[col].map(freq).fillna(0.0)
		test_out[f"{col}_freq"] = test_out[col].map(freq).fillna(0.0)

	return train_out, test_out, encoders


def build_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
	"""Return model-ready X and y."""
	feature_cols = [
		"price",
		"original_price",
		"discount_rate",
		"rating_average",
		"Price_Gap",
		"brand_freq",
		"category_freq",
	]
	X = df[feature_cols].copy()
	y = df[TARGET_COL].copy()
	return X, y


def train_xgboost_classifier(X_train: pd.DataFrame, y_train: pd.Series) -> XGBClassifier:
	"""Train XGBoost with imbalance-aware weighting."""
	positive = int((y_train == 1).sum())
	negative = int((y_train == 0).sum())
	scale_pos_weight = (negative / positive) if positive > 0 else 1.0

	model = XGBClassifier(
		n_estimators=350,
		max_depth=5,
		learning_rate=0.05,
		subsample=0.9,
		colsample_bytree=0.9,
		reg_alpha=0.2,
		reg_lambda=1.0,
		min_child_weight=3,
		objective="binary:logistic",
		eval_metric="auc",
		scale_pos_weight=scale_pos_weight,
		random_state=RANDOM_STATE,
		n_jobs=-1,
	)
	model.fit(X_train, y_train)
	return model


def evaluate_model(
	model: XGBClassifier,
	X_test: pd.DataFrame,
	y_test: pd.Series,
) -> dict[str, object]:
	"""Compute confusion matrix, ROC-AUC, and related diagnostics."""
	y_proba = model.predict_proba(X_test)[:, 1]
	y_pred = (y_proba >= 0.5).astype(int)

	cm = confusion_matrix(y_test, y_pred)
	auc = roc_auc_score(y_test, y_proba)
	fpr, tpr, thresholds = roc_curve(y_test, y_proba)
	report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

	return {
		"confusion_matrix": cm,
		"roc_auc": float(auc),
		"fpr": fpr,
		"tpr": tpr,
		"thresholds": thresholds,
		"classification_report": report,
		"y_proba": y_proba,
	}


def compute_shap_values(model: XGBClassifier, X_train: pd.DataFrame) -> np.ndarray:
	"""Compute SHAP values for tree model."""
	explainer = shap.TreeExplainer(model)
	shap_values = explainer.shap_values(X_train)
	return np.asarray(shap_values)


def save_roc_auc_plot(fpr: np.ndarray, tpr: np.ndarray, roc_auc: float, out_path: Path) -> None:
	"""Save ROC curve figure."""
	plt.figure(figsize=(7, 5))
	plt.plot(fpr, tpr, linewidth=2, label=f"ROC curve (AUC = {roc_auc:.4f})")
	plt.plot([0, 1], [0, 1], linestyle="--", linewidth=1)
	plt.xlabel("False Positive Rate")
	plt.ylabel("True Positive Rate")
	plt.title("ROC-AUC Curve - Tiki Best-Seller Classifier")
	plt.legend(loc="lower right")
	plt.tight_layout()
	plt.savefig(out_path, dpi=150)
	plt.close()


def save_shap_summary_plot(shap_values: np.ndarray, X_train: pd.DataFrame, out_path: Path) -> None:
	"""Save SHAP summary plot to image."""
	plt.figure(figsize=(9, 6))
	shap.summary_plot(shap_values, X_train, show=False)
	plt.tight_layout()
	plt.savefig(out_path, dpi=150, bbox_inches="tight")
	plt.close()


def save_artifacts(
	models_dir: Path,
	model: XGBClassifier,
	conf_matrix: np.ndarray,
	shap_values: np.ndarray,
	metrics_payload: dict[str, object],
	encoders: dict[str, dict[str, float]],
) -> None:
	"""Persist required and supporting artifacts."""
	models_dir.mkdir(parents=True, exist_ok=True)

	model_path = models_dir / "xgboost_tiki.pkl"
	cm_path = models_dir / "confusion_matrix.npy"
	shap_path = models_dir / "shap_values.pkl"
	metrics_path = models_dir / "metrics.json"
	encoders_path = models_dir / "encoders.pkl"

	joblib.dump(model, model_path)
	np.save(cm_path, conf_matrix)
	with open(shap_path, "wb") as f:
		pickle.dump(shap_values, f)

	serializable_metrics = {
		"roc_auc": float(metrics_payload["roc_auc"]),
		"classification_report": metrics_payload["classification_report"],
	}
	with open(metrics_path, "w", encoding="utf-8") as f:
		json.dump(serializable_metrics, f, ensure_ascii=False, indent=2)

	joblib.dump(encoders, encoders_path)


def run_pipeline(
	data_dir: Path | None = None,
	models_dir: Path | None = None,
) -> dict[str, object]:
	"""Execute the full training + explainability pipeline."""
	root_dir = Path(__file__).resolve().parents[1]
	data_dir = data_dir or (root_dir / "data" / "processed")
	models_dir = models_dir or (root_dir / "models")

	df_joined = load_and_join_data(data_dir)
	df_model = preprocess_and_engineer_features(df_joined)

	train_df, test_df = train_test_split(
		df_model,
		test_size=0.2,
		random_state=RANDOM_STATE,
		stratify=df_model[TARGET_COL],
	)

	train_df, test_df, encoders = add_frequency_encoding(train_df, test_df)

	X_train, y_train = build_feature_matrix(train_df)
	X_test, y_test = build_feature_matrix(test_df)

	model = train_xgboost_classifier(X_train, y_train)
	eval_payload = evaluate_model(model, X_test, y_test)
	shap_values = compute_shap_values(model, X_train)

	save_artifacts(
		models_dir=models_dir,
		model=model,
		conf_matrix=eval_payload["confusion_matrix"],
		shap_values=shap_values,
		metrics_payload=eval_payload,
		encoders=encoders,
	)

	save_roc_auc_plot(
		eval_payload["fpr"],
		eval_payload["tpr"],
		float(eval_payload["roc_auc"]),
		models_dir / "roc_auc_curve.png",
	)
	save_shap_summary_plot(shap_values, X_train, models_dir / "shap_summary.png")

	return {
		"rows_total": int(len(df_model)),
		"rows_train": int(len(train_df)),
		"rows_test": int(len(test_df)),
		"positive_rate": float(df_model[TARGET_COL].mean()),
		"roc_auc": float(eval_payload["roc_auc"]),
		"models_dir": str(models_dir),
	}


if __name__ == "__main__":
	summary = run_pipeline()
	print("Training completed.")
	print(json.dumps(summary, indent=2))
