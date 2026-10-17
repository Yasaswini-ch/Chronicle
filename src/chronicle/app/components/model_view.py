"""Model comparison and evaluation component for Streamlit."""

from __future__ import annotations

import streamlit as st
import pandas as pd
from chronicle.classifier.classical import ClassicalClassifier
from chronicle.classifier.neural import NeuralClassifier
from chronicle.classifier.evaluator import ClassifierEvaluator


def render_model_view(myths: list[dict], sbert=None) -> None:
    """Render the machine learning classifier comparison view."""
    st.markdown(
        '<div style="margin-bottom: 1.5rem;">'
        '<h2 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; margin-bottom: 0.25rem;">Linguistic Models & Classification Benchmarks</h2>'
        '<p style="color: #9BA3AF; font-size: 0.95rem; font-family: Georgia, serif;">'
        'Empirical evaluation of sparse n-gram feature models (Logistic Regression, Linear SVM, Multinomial Naive Bayes) '
        'versus a deep neural multi-layer perceptron trained on dense contextual embeddings.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    if not myths or len(myths) < 6:
        st.warning("Insufficient myth samples to run full cross-evaluation.")
        return

    texts = [m.get("text", "") for m in myths]
    labels = [m.get("theme", "hubris") for m in myths]

    if st.button("Execute Cross-Model Benchmark Suite", type="primary"):
        evaluator = ClassifierEvaluator()
        results = {}

        with st.spinner("Training Classical Models (TF-IDF + LogReg, SVM, Naive Bayes)..."):
            for m_type in ["logistic_regression", "svm", "naive_bayes"]:
                clf = ClassicalClassifier(model_type=m_type)
                metrics = clf.train(texts, labels, test_size=0.25)
                results[m_type.replace("_", " ").title()] = metrics

        with st.spinner("Training Neural MLP on SBERT embeddings (PyTorch)..."):
            if sbert is not None:
                embeddings = sbert.encode(texts)
            else:
                embeddings = texts
            neural_clf = NeuralClassifier(epochs=35, batch_size=8)
            neural_metrics = neural_clf.train(embeddings, labels, val_split=0.25)
            results["Neural MLP (SBERT)"] = neural_metrics

        st.session_state["benchmark_results"] = results

    results = st.session_state.get("benchmark_results")
    if results:
        evaluator = ClassifierEvaluator()
        df = evaluator.compare_models(results)
        st.markdown(
            '<h3 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
            'color: #E8E2D8; font-size: 1.15rem; margin-top: 1.5rem;">Benchmark Performance Metrics</h3>',
            unsafe_allow_html=True,
        )
        st.dataframe(df, use_container_width=True)

        chart_fig = evaluator.plot_comparison_chart(results)
        chart_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(24, 27, 31, 0.6)",
            plot_bgcolor="rgba(24, 27, 31, 0.4)",
            font=dict(family="Georgia, serif", color="#DCD6CD"),
        )
        st.plotly_chart(chart_fig, use_container_width=True)

        best_m = evaluator.best_model(results, metric="f1")
        st.markdown(
            f'<div style="border-left: 2px solid #C5A059; background: #171A1E; padding: 10px 14px; margin-top: 12px; color: #E8E2D8;">'
            f'<b>Optimal Macro-F1 Classifier Architecture:</b> {best_m}'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.expander("Detailed Metric Classification Report"):
            report = evaluator.generate_report(results)
            st.text(report)
