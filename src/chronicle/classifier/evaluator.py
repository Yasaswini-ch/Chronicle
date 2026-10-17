"""Model comparison and evaluation utilities for Chronicle classifiers.

Provides side-by-side metric comparison, confusion matrix visualisations,
bar charts, and text reports across multiple classifiers.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class ClassifierEvaluator:
    """Compare and visualise results from multiple classifiers.

    All public methods accept a *results* dictionary keyed by model name,
    where each value is a metrics dictionary containing at minimum
    ``accuracy`` and ``f1_macro``.

    Examples
    --------
    >>> evaluator = ClassifierEvaluator()
    >>> df = evaluator.compare_models({
    ...     "Logistic Regression": lr_metrics,
    ...     "SVM": svm_metrics,
    ...     "Neural MLP": neural_metrics,
    ... })
    """

    # ------------------------------------------------------------------
    # Tabular comparison
    # ------------------------------------------------------------------

    def compare_models(
        self, results: dict[str, dict[str, Any]],
    ) -> pd.DataFrame:
        """Build a comparison DataFrame from model result dicts.

        Parameters
        ----------
        results : dict[str, dict]
            Mapping of ``model_name → metrics_dict``.  Each metrics dict
            must contain ``accuracy`` and ``f1_macro``; optional keys
            ``precision`` and ``recall`` are extracted from the
            ``classification_report`` if present.

        Returns
        -------
        pd.DataFrame
            One row per model with columns for every metric.
        """
        rows: list[dict[str, Any]] = []
        for name, metrics in results.items():
            row: dict[str, Any] = {"model": name}
            row["accuracy"] = metrics.get("accuracy", np.nan)
            row["f1_macro"] = metrics.get("f1_macro", np.nan)

            # Try to pull precision/recall from the classification report
            report = metrics.get("classification_report", {})
            if isinstance(report, dict):
                macro_avg = report.get("macro avg", {})
                row["precision_macro"] = macro_avg.get("precision", np.nan)
                row["recall_macro"] = macro_avg.get("recall", np.nan)
                weighted_avg = report.get("weighted avg", {})
                row["f1_weighted"] = weighted_avg.get("f1-score", np.nan)

            rows.append(row)

        df = pd.DataFrame(rows).set_index("model")
        logger.info("Comparison table:\n%s", df.to_string())
        return df

    # ------------------------------------------------------------------
    # Confusion matrices
    # ------------------------------------------------------------------

    def plot_confusion_matrices(
        self,
        results: dict[str, dict[str, Any]],
        class_names: list[str],
    ) -> go.Figure:
        """Create side-by-side confusion matrix heatmaps.

        Parameters
        ----------
        results : dict[str, dict]
            Each value must include ``confusion_matrix`` as a list-of-lists
            or 2-D array.
        class_names : list[str]
            Ordered list of class labels for axis tick labels.

        Returns
        -------
        plotly.graph_objects.Figure
            Plotly figure with one subplot per model.
        """
        model_names = list(results.keys())
        n_models = len(model_names)

        fig = make_subplots(
            rows=1,
            cols=n_models,
            subplot_titles=model_names,
            horizontal_spacing=0.08,
        )

        for idx, name in enumerate(model_names, start=1):
            cm = np.array(results[name].get("confusion_matrix", []))
            if cm.size == 0:
                logger.warning("No confusion matrix for '%s'; skipping.", name)
                continue

            # Normalise rows to percentages for colour scale
            row_sums = cm.sum(axis=1, keepdims=True)
            cm_norm = np.where(row_sums > 0, cm / row_sums, 0.0)

            # Build annotation text (raw counts)
            text = [[str(int(v)) for v in row] for row in cm]

            fig.add_trace(
                go.Heatmap(
                    z=cm_norm,
                    x=class_names,
                    y=class_names,
                    text=text,
                    texttemplate="%{text}",
                    colorscale="Blues",
                    showscale=(idx == n_models),
                    hovertemplate=(
                        "True: %{y}<br>Predicted: %{x}<br>"
                        "Count: %{text}<br>Rate: %{z:.2f}<extra></extra>"
                    ),
                ),
                row=1,
                col=idx,
            )
            fig.update_xaxes(title_text="Predicted", row=1, col=idx)
            fig.update_yaxes(title_text="True", row=1, col=idx)

        fig.update_layout(
            title_text="Confusion Matrices — Model Comparison",
            height=450,
            width=max(400 * n_models, 600),
        )
        return fig

    # ------------------------------------------------------------------
    # Bar chart comparison
    # ------------------------------------------------------------------

    def plot_comparison_chart(
        self, results: dict[str, dict[str, Any]],
    ) -> go.Figure:
        """Bar chart comparing accuracy and F1 across models.

        Parameters
        ----------
        results : dict[str, dict]
            Each value must contain ``accuracy`` and ``f1_macro``.

        Returns
        -------
        plotly.graph_objects.Figure
            Grouped bar chart.
        """
        model_names = list(results.keys())
        accuracies = [results[n].get("accuracy", 0) for n in model_names]
        f1_scores = [results[n].get("f1_macro", 0) for n in model_names]

        fig = go.Figure(
            data=[
                go.Bar(
                    name="Accuracy",
                    x=model_names,
                    y=accuracies,
                    text=[f"{v:.3f}" for v in accuracies],
                    textposition="auto",
                    marker_color="#636EFA",
                ),
                go.Bar(
                    name="F1 Macro",
                    x=model_names,
                    y=f1_scores,
                    text=[f"{v:.3f}" for v in f1_scores],
                    textposition="auto",
                    marker_color="#EF553B",
                ),
            ],
        )
        fig.update_layout(
            title_text="Model Performance Comparison",
            xaxis_title="Model",
            yaxis_title="Score",
            yaxis_range=[0, 1.05],
            barmode="group",
            height=450,
            width=max(300 * len(model_names), 500),
        )
        return fig

    # ------------------------------------------------------------------
    # Text report
    # ------------------------------------------------------------------

    def generate_report(
        self, results: dict[str, dict[str, Any]],
    ) -> str:
        """Generate a human-readable text report comparing models.

        Parameters
        ----------
        results : dict[str, dict]
            Full results dictionary keyed by model name.

        Returns
        -------
        str
            Multi-line text summary.
        """
        lines: list[str] = [
            "=" * 64,
            "CHRONICLE — Classifier Comparison Report",
            "=" * 64,
            "",
        ]

        # Per-model summaries
        for name, metrics in results.items():
            lines.append(f"Model: {name}")
            lines.append("-" * 40)
            lines.append(f"  Accuracy  : {metrics.get('accuracy', 'N/A'):.4f}"
                         if isinstance(metrics.get("accuracy"), (int, float))
                         else f"  Accuracy  : N/A")
            lines.append(f"  F1 (macro): {metrics.get('f1_macro', 'N/A'):.4f}"
                         if isinstance(metrics.get("f1_macro"), (int, float))
                         else f"  F1 (macro): N/A")

            report = metrics.get("classification_report", {})
            if isinstance(report, dict):
                macro_avg = report.get("macro avg", {})
                lines.append(
                    f"  Precision : {macro_avg.get('precision', 'N/A'):.4f}"
                    if isinstance(macro_avg.get("precision"), (int, float))
                    else "  Precision : N/A"
                )
                lines.append(
                    f"  Recall    : {macro_avg.get('recall', 'N/A'):.4f}"
                    if isinstance(macro_avg.get("recall"), (int, float))
                    else "  Recall    : N/A"
                )
            lines.append("")

        # Winner summary
        if results:
            best_acc_name = max(results, key=lambda n: results[n].get("accuracy", -1))
            best_f1_name = max(results, key=lambda n: results[n].get("f1_macro", -1))
            lines.append("Summary")
            lines.append("-" * 40)
            lines.append(
                f"  Best accuracy  : {best_acc_name} "
                f"({results[best_acc_name].get('accuracy', 0):.4f})"
            )
            lines.append(
                f"  Best F1 (macro): {best_f1_name} "
                f"({results[best_f1_name].get('f1_macro', 0):.4f})"
            )
            lines.append("")

        lines.append("=" * 64)
        report_text = "\n".join(lines)
        logger.info("Report generated (%d chars)", len(report_text))
        return report_text

    def generate_comparison_report(
        self, results: dict[str, dict[str, Any]]
    ) -> str:
        """Alias for generate_report."""
        return self.generate_report(results)

    def best_model(
        self, results: dict[str, dict[str, Any]], metric: str = "f1"
    ) -> str:
        """Return the name of the best performing model based on *metric*."""
        if not results:
            raise ValueError("No model results provided.")

        def get_score(m: dict[str, Any]) -> float:
            if metric == "f1":
                return float(m.get("f1", m.get("f1_macro", -1.0)))
            return float(m.get(metric, -1.0))

        return max(results, key=lambda name: get_score(results[name]))

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return "ClassifierEvaluator()"
