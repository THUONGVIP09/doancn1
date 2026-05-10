import tensorflow as tf

model = tf.keras.models.load_model(
    "model_outputs/models/cnn_model.keras",
    compile=False
)

model.save("model_outputs/models/cnn_model.h5")

print("Converted successfully: model_outputs/models/cnn_model.h5")