from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *
from keras.regularizers import l2
#from theano.tensor import lt

def example(num_inputs, num_outputs):
    """
    Example Keras model
    """
    model = Sequential()
    model.add(
        Dense(
            10, kernel_initializer="glorot_normal", activation="relu", input_dim=num_inputs))
    model.add(Dense(num_outputs, kernel_initializer="glorot_uniform", activation="softmax"))
    model.compile(
        loss="categorical_crossentropy",
        optimizer=Adam(),
        metrics=[
            "categorical_accuracy",
        ])
    return model


def smhtt_simple(num_inputs, num_outputs):
    model = Sequential()
    model.add(
        Dense(
            100, kernel_initializer="glorot_normal", activation="tanh",
            input_dim=num_inputs))
    model.add(Dense(num_outputs, kernel_initializer="glorot_normal", activation="softmax"))
    model.compile(loss="mean_squared_error", optimizer=Nadam(), metrics=[])
    return model


def smhtt_mt(num_inputs, num_outputs):
    model = Sequential()
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="tanh",
            kernel_regularizer=l2(1e-4),
            input_dim=num_inputs))
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="tanh",
            kernel_regularizer=l2(1e-4)))
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="tanh",
            kernel_regularizer=l2(1e-4)))
    model.add(
        Dense(
            num_outputs, kernel_initializer="glorot_normal", activation="softmax"))
    model.compile(loss="mean_squared_error", optimizer=Adam(), metrics=['accuracy'])
    return model


def smhtt_et(num_inputs, num_outputs):
    model = Sequential()
    model.add(
        Dense(
            1000, kernel_initializer="glorot_normal", activation="tanh",
            kernel_regularizer=l2(1e-4),
            input_dim=num_inputs))
    model.add(
        Dense(
            num_outputs, init="glorot_normal", activation="softmax"))
    model.compile(loss="mean_squared_error", optimizer=Nadam(), metrics=[])
    return model


def smhtt_tt(num_inputs, num_outputs):
    model = Sequential()
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="tanh",
            kernel_regularizer=l2(1e-4),
            input_dim=num_inputs))
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="tanh",
            kernel_regularizer=l2(1e-4)))
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="tanh",
            kernel_regularizer=l2(1e-4)))
    model.add(
        Dense(
            num_outputs, kernel_initializer="glorot_normal", activation="softmax"))
    model.compile(loss="mean_squared_error", optimizer=Nadam(), metrics=[])
    return model


def smhtt_legacy(num_inputs, num_outputs):
    model = Sequential()
    model.add(
        Dense(
            300,
            kernel_initializer="glorot_normal",
            activation="relu",
            kernel_regularizer=l2(1e-4),
            input_dim=num_inputs))
    model.add(
        Dense(
            300,
            kernel_initializer="glorot_normal",
            activation="relu",
            kernel_regularizer=l2(1e-4)))
    model.add(
        Dense(
            300,
            kernel_initializer="glorot_normal",
            activation="relu",
            kernel_regularizer=l2(1e-4)))
    model.add(
        Dense(
            num_outputs,
            kernel_initializer="glorot_normal",
            activation="softmax"))
    model.compile(
        loss="mean_squared_error",
        optimizer=Adam(),
        metrics=[])
    return model

def smhtt_dropout(num_inputs, num_outputs):
    model = Sequential()

    for i, nodes in enumerate([200] * 2):
        if i == 0:
            model.add(Dense(nodes, input_dim=num_inputs))
        else:
            model.add(Dense(nodes))
        # model.add(BatchNormalization(axis=1))
        model.add(Activation("relu"))
        model.add(Dropout(0.5))

    model.add(Dense(num_outputs))
    model.add(Activation("softmax"))

    model.compile(loss="mean_squared_error", optimizer=Nadam(), metrics=['categorical_accuracy'])
    return model

def smhtt_dropout_tanh_batchnorm(num_inputs, num_outputs):
    model = Sequential()

    for i, nodes in enumerate([200] * 2):
        if i == 0:
            model.add(Dense(nodes, kernel_regularizer=l2(1e-5), input_dim=num_inputs))
        else:
            model.add(Dense(nodes, kernel_regularizer=l2(1e-5)))
        model.add(BatchNormalization(axis=1))
        model.add(Activation("tanh"))
        model.add(Dropout(0.3))

    model.add(Dense(num_outputs, kernel_regularizer=l2(1e-5)))
    model.add(Activation("softmax"))

    model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=1e-4), metrics=['categorical_accuracy'])
    return model
    
def smhtt_dropout_tanh(num_inputs, num_outputs):
    model = Sequential()

    for i, nodes in enumerate([200] * 2):
        if i == 0:
            model.add(Dense(nodes, kernel_regularizer=l2(1e-5), input_dim=num_inputs))
        else:
            model.add(Dense(nodes, kernel_regularizer=l2(1e-5)))
        model.add(Activation("tanh"))
        model.add(Dropout(0.3))

    model.add(Dense(num_outputs, kernel_regularizer=l2(1e-5)))
    model.add(Activation("softmax"))

    model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=1e-4), metrics=['categorical_accuracy'])
    return model

def smhtt_dropout_selu(num_inputs, num_outputs):
    model = Sequential()

    for i, nodes in enumerate([200] * 2):
        if i == 0:
            model.add(Dense(nodes, kernel_regularizer=l2(1e-5), input_dim=num_inputs))
        else:
            model.add(Dense(nodes, kernel_regularizer=l2(1e-5)))
        model.add(Activation("selu"))
        model.add(Dropout(0.3))

    model.add(Dense(num_outputs, kernel_regularizer=l2(1e-5)))
    model.add(Activation("softmax"))

    model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=1e-4), metrics=['categorical_accuracy'])
    return model

def smhtt_alpha_dropout_selu_lecun(num_inputs, num_outputs):
    model = Sequential()

    for i, nodes in enumerate([200] * 2):
        if i == 0:
            model.add(Dense(nodes, kernel_initializer="lecun_normal", kernel_regularizer=l2(1e-5), input_dim=num_inputs))
        else:
            model.add(Dense(nodes, kernel_initializer="lecun_normal", kernel_regularizer=l2(1e-5)))
        model.add(Activation("selu"))
        model.add(AlphaDropout(0.1))

    model.add(Dense(num_outputs, kernel_initializer="lecun_normal", kernel_regularizer=l2(1e-5)))
    model.add(Activation("softmax"))

    model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=1e-4), metrics=['categorical_accuracy'])
    return model

def smhtt_em(num_inputs, num_outputs):
    model = Sequential()
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="relu",
            kernel_regularizer=l2(1e-4),input_dim=num_inputs) )
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="relu",
            kernel_regularizer=l2(1e-4),input_dim=num_inputs) )
    model.add(
        Dense(
            300, kernel_initializer="glorot_normal", activation="relu",
            kernel_regularizer=l2(1e-4),input_dim=num_inputs) )
    model.add(
        Dense(
            num_outputs, kernel_initializer="glorot_normal", activation="softmax"))
    model.compile(loss="mean_squared_error", optimizer=Nadam(), metrics=[])
    return model
