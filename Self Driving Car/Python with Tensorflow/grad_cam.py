import tensorflow as tf
import numpy as np
import cv2

def compute_gradcam(model, img_array, last_conv_layer_name="conv2d_3"):
    eps=1e-8
    # construct our gradient model by supplying (1) the inputs
    # to our pre-trained model, (2) the output of the (presumably)
    # final 4D layer in the network, and (3) the output of the
    # softmax activations from the model
    gradModel = tf.keras.models.Model(
        inputs=[model.inputs],
        outputs=[model.get_layer(last_conv_layer_name).output,
            model.output])
    
    # record operations for automatic differentiation
    with tf.GradientTape() as tape:
        # cast the image tensor to a float-32 data type, pass the
        # image through the gradient model, and grab the loss
        # associated with the specific class index
        inputs = tf.cast(img_array, tf.float32)
        (convOutputs, predictions) = gradModel(inputs)
        loss = predictions[:, 0]
    # use automatic differentiation to compute the gradients
    grads = tape.gradient(loss, convOutputs)   
    

    # compute the guided gradients
    castConvOutputs = tf.cast(convOutputs > 0, "float32")
    castGrads = tf.cast(grads > 0, "float32")
    guidedGrads = castConvOutputs * castGrads * grads
    # the convolution and guided gradients have a batch dimension
    # (which we don't need) so let's grab the volume itself and
    # discard the batch
    convOutputs = convOutputs[0]
    guidedGrads = guidedGrads[0]

    # compute the average of the gradient values, and using them
    # as weights, compute the ponderation of the filters with
    # respect to the weights
    weights = tf.reduce_mean(guidedGrads, axis=(0, 1))
    cam = tf.reduce_sum(tf.multiply(weights, convOutputs), axis=-1)

    # grab the spatial dimensions of the input image and resize
    # the output class activation map to match the input image
    # dimensions
    (w, h) = (img_array.shape[2], img_array.shape[1])
    heatmap = cv2.resize(cam.numpy(), (w, h))
    # normalize the heatmap such that all values lie in the range
    # [0, 1], scale the resulting values to the range [0, 255],
    # and then convert to an unsigned 8-bit integer
    numer = heatmap - np.min(heatmap)
    denom = (heatmap.max() - heatmap.min()) + eps
    heatmap = numer / denom
    heatmap = (heatmap * 255).astype("uint8")
    # return the resulting heatmap to the calling function
    return heatmap

    """# 1. Create a model that maps input to the last conv layer and the final output
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )
    print("Image SHape Before Grad Cam:", img_array.shape)
    img_array = img_array.astype('float32')

    # 2. Record gradients of the steering output w.r.t. the last conv feature map
    with tf.GradientTape() as tape:
        last_conv_layer_output, steering_prediction = grad_model(img_array)
        print("Last Conv Layer Output Shape:", last_conv_layer_output.shape)
        print("Steering Prediction Shape:", steering_prediction.shape)
        # We target the specific steering value (index 0 of the output)
        target_output = steering_prediction[:, 0]
        print("Target Output Shape:", target_output.shape)

    # 3. Calculate gradients and pool them (Global Average Pooling of gradients)
    grads = tape.gradient(target_output, last_conv_layer_output)
    print("Gradients Shape:", grads.shape)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    print("Pooled Gradients Shape:", pooled_grads.shape)

    # 4. Weight the feature maps by the pooled gradients
    last_conv_layer_output = last_conv_layer_output[0]
    print("Last Conv Layer Output Squeezed Shape:", last_conv_layer_output.shape)
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    print("Heatmap Shape Before Squeeze:", heatmap.shape)
    heatmap = tf.squeeze(heatmap)
    print("Heatmap Shape After Squeeze:", heatmap.shape)

    # 5. Normalize between 0 and 1 for visualization
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
    return heatmap.numpy()"""

import tensorflow as tf
import numpy as np
import cv2

def compute_gradcam_regression(model, img_array, angle,
                               last_conv_layer_name="conv2d_2"):
    eps = 1e-8

    gradModel = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[
            model.get_layer(last_conv_layer_name).output,
            model.output
        ],
    )

    with tf.GradientTape() as tape:
        inputs = tf.cast(img_array, tf.float32)
        convOutputs, prediction = gradModel(inputs)
        STRAIGHT_THRESH = 0.1
        # steering-conditioned target
        if angle > STRAIGHT_THRESH:
            loss = prediction
        elif angle < -STRAIGHT_THRESH:
            loss = -prediction
        else:
            loss = tf.math.abs(prediction)

    grads = tape.gradient(loss, convOutputs)

    # remove batch dimension
    convOutputs = convOutputs[0]
    grads = grads[0]

    # channel importance weights
    weights = tf.reduce_mean(grads, axis=(0, 1))

    cam = tf.reduce_sum(weights * convOutputs, axis=-1)

    # optional: keep only positive influence
    #cam = tf.nn.relu(cam)

    heatmap = cv2.resize(
        cam.numpy(),
        (img_array.shape[2], img_array.shape[1])
    )

    #heatmap = (heatmap - heatmap.min()) / (heatmap.max() + eps)
    #heatmap = (heatmap * 255).astype("uint8")

    return heatmap