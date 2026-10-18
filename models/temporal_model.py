"""
CardioTwin — Temporal Model (Bi-LSTM with Attention)
=====================================================
Processes wearable sensor time-series data through a bidirectional LSTM
with self-attention mechanism to detect temporal anomaly patterns
preceding cardiovascular events.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, callbacks, Model
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


SAVED_DIR = os.path.join(os.path.dirname(__file__), "saved")


class AttentionLayer(layers.Layer):
    """
    Self-attention layer for sequence models.
    Learns to focus on the most relevant timesteps in the input sequence.
    """

    def __init__(self, units=64, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.W = self.add_weight(
            name="attention_weight",
            shape=(input_shape[-1], self.units),
            initializer="glorot_uniform",
            trainable=True
        )
        self.b = self.add_weight(
            name="attention_bias",
            shape=(self.units,),
            initializer="zeros",
            trainable=True
        )
        self.V = self.add_weight(
            name="attention_context",
            shape=(self.units, 1),
            initializer="glorot_uniform",
            trainable=True
        )

    def call(self, inputs):
        # inputs shape: (batch_size, timesteps, features)
        score = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        attention_weights = tf.nn.softmax(tf.tensordot(score, self.V, axes=1), axis=1)
        context_vector = tf.reduce_sum(inputs * attention_weights, axis=1)
        return context_vector, tf.squeeze(attention_weights, axis=-1)

    def get_config(self):
        config = super().get_config()
        config.update({"units": self.units})
        return config


def build_temporal_model(input_shape, lstm_units=128, attention_units=64,
                         dense_units=64, dropout_rate=0.3):
    """Build the Bi-LSTM with Attention temporal model."""
    inputs = keras.Input(shape=input_shape, name="wearable_input")

    # Bidirectional LSTM layer 1
    x = layers.Bidirectional(
        layers.LSTM(lstm_units, return_sequences=True, name="lstm_1"),
        name="bi_lstm_1"
    )(inputs)
    x = layers.Dropout(dropout_rate, name="dropout_1")(x)

    # Bidirectional LSTM layer 2
    x = layers.Bidirectional(
        layers.LSTM(lstm_units // 2, return_sequences=True, name="lstm_2"),
        name="bi_lstm_2"
    )(x)
    x = layers.Dropout(dropout_rate, name="dropout_2")(x)

    # Attention mechanism
    attention_layer = AttentionLayer(units=attention_units, name="attention")
    context_vector, attention_weights = attention_layer(x)

    # Dense layers
    x = layers.Dense(dense_units, activation="relu", name="dense_1")(context_vector)
    x = layers.BatchNormalization(name="batch_norm")(x)
    x = layers.Dropout(dropout_rate, name="dropout_3")(x)
    x = layers.Dense(dense_units // 2, activation="relu", name="dense_2")(x)

    # Output
    output = layers.Dense(1, activation="sigmoid", name="risk_output")(x)

    model = Model(inputs=inputs, outputs=output, name="CardioTwin_Temporal")
    return model


def train_temporal_model(temporal_data, epochs=50, batch_size=32, learning_rate=1e-3):
    """Train the temporal model on wearable sensor windows."""
    os.makedirs(SAVED_DIR, exist_ok=True)

    X_train = temporal_data["X_train"]
    X_val = temporal_data["X_val"]
    y_train = temporal_data["y_train"]
    y_val = temporal_data["y_val"]

    input_shape = (X_train.shape[1], X_train.shape[2])
    print(f"\n🧠 Building Temporal Model (Bi-LSTM + Attention)")
    print(f"  Input shape: {input_shape}")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Validation samples: {len(X_val)}")

    model = build_temporal_model(input_shape)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.AUC(name="auroc"),
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ]
    )
    model.summary()

    # Handle class imbalance with class weights
    n_pos = y_train.sum()
    n_neg = len(y_train) - n_pos
    class_weight = {0: 1.0, 1: max(1.0, n_neg / max(n_pos, 1))}
    print(f"\n  Class weights: {class_weight}")

    # Callbacks
    cb = [
        callbacks.EarlyStopping(
            monitor="val_auroc", mode="max", patience=10,
            restore_best_weights=True, verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5,
            min_lr=1e-6, verbose=1
        ),
        callbacks.ModelCheckpoint(
            os.path.join(SAVED_DIR, "lstm_model_best.keras"),
            monitor="val_auroc", mode="max",
            save_best_only=True, verbose=0
        ),
    ]

    # Train
    print(f"\n🏋️ Training for up to {epochs} epochs...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=cb,
        verbose=1
    )

    # Save final model
    model.save(os.path.join(SAVED_DIR, "lstm_model.keras"))
    print(f"  ✓ Model saved to {SAVED_DIR}/lstm_model.keras")

    # Plot training curves
    plot_training_history(history)

    return model, history


def plot_training_history(history):
    """Save training history plots."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Loss
    axes[0].plot(history.history["loss"], label="Train", linewidth=2)
    axes[0].plot(history.history["val_loss"], label="Val", linewidth=2)
    axes[0].set_title("Loss", fontweight="bold")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # AUROC
    axes[1].plot(history.history["auroc"], label="Train", linewidth=2)
    axes[1].plot(history.history["val_auroc"], label="Val", linewidth=2)
    axes[1].set_title("AUROC", fontweight="bold")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # Precision / Recall
    axes[2].plot(history.history["precision"], label="Precision (Train)", linewidth=2)
    axes[2].plot(history.history["recall"], label="Recall (Train)", linewidth=2)
    axes[2].plot(history.history["val_precision"], label="Precision (Val)", linewidth=2, linestyle="--")
    axes[2].plot(history.history["val_recall"], label="Recall (Val)", linewidth=2, linestyle="--")
    axes[2].set_title("Precision & Recall", fontweight="bold")
    axes[2].set_xlabel("Epoch")
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(SAVED_DIR, "temporal_training_curves.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Training curves saved to {SAVED_DIR}/temporal_training_curves.png")
