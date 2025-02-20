import copy
from abc import abstractmethod
import unittest
import numpy as np

from si.neural_networks.optimizers import Optimizer


class Layer:
    """
    Base class for neural network layers.
    """

    @abstractmethod
    def forward_propagation(self, input: np.ndarray, training: bool) -> np.ndarray:
        """
        Perform forward propagation on the given input, i.e., computes the output of a layer for a given input.

        Parameters
        ----------
        input: numpy.ndarray
            The input to the layer.
        training: bool
            Whether the layer is in training mode or in inference mode.

        Returns
        -------
        numpy.ndarray
            The output of the layer.
        """
        raise NotImplementedError

    @abstractmethod
    def backward_propagation(self, output_error: float) -> float:
        """
        Perform backward propagation on the given output error, i.e., computes dE/dX for a given dE/dY and update
        parameters if any.

        Parameters
        ----------
        output_error: float
            The output error of the layer.

        Returns
        -------
        float
            The input error of the layer.
        """
        raise NotImplementedError

    def layer_name(self) -> str:
        """
        Returns the name of the layer.

        Returns
        -------
        str
            The name of the layer.
        """
        return self.__class__.__name__

    @abstractmethod
    def output_shape(self) -> tuple:
        """
        Returns the shape of the output of the layer.

        Returns
        -------
        tuple
            The shape of the output of the layer.
        """
        raise NotImplementedError

    def set_input_shape(self, shape: tuple):
        """
        Sets the shape of the input to the layer.

        Parameters
        ----------
        shape: tuple
            The shape of the input to the layer.
        """
        self._input_shape = shape

    def input_shape(self) -> tuple:
        """
        Returns the shape of the input to the layer.

        Returns
        -------
        tuple
            The shape of the input to the layer.
        """
        return self._input_shape

    @abstractmethod
    def parameters(self) -> int:
        """
        Returns the number of parameters of the layer.

        Returns
        -------
        int
            The number of parameters of the layer.
        """
        raise NotImplementedError


class DenseLayer(Layer):
    """
    Dense layer of a neural network.
    """

    def __init__(self, n_units: int, input_shape: tuple = None):
        """
        Initialize the dense layer.

        Parameters
        ----------
        n_units: int
            The number of units of the layer, aka the number of neurons, aka the dimensionality of the output space.
        input_shape: tuple
            The shape of the input to the layer.
        """
        super().__init__()
        self.n_units = n_units
        self._input_shape = input_shape

        self.input = None
        self.output = None
        self.weights = None
        self.biases = None

    def initialize(self, optimizer: Optimizer) -> 'DenseLayer':
        # initialize weights from a 0 centered uniform distribution [-0.5, 0.5)
        self.weights = np.random.rand(self.input_shape()[0], self.n_units) - 0.5
        # initialize biases to 0
        self.biases = np.zeros((1, self.n_units))
        self.w_opt = copy.deepcopy(optimizer)
        self.b_opt = copy.deepcopy(optimizer)
        return self

    def parameters(self) -> int:
        """
        Returns the number of parameters of the layer.

        Returns
        -------
        int
            The number of parameters of the layer.
        """
        return np.prod(self.weights.shape) + np.prod(self.biases.shape)

    def forward_propagation(self, input: np.ndarray, training: bool) -> np.ndarray:
        """
        Perform forward propagation on the given input.

        Parameters
        ----------
        input: numpy.ndarray
            The input to the layer.
        training: bool
            Whether the layer is in training mode or in inference mode.

        Returns
        -------
        numpy.ndarray
            The output of the layer.
        """
        self.input = input
        self.output = np.dot(self.input, self.weights) + self.biases
        return self.output

    def backward_propagation(self, output_error: np.ndarray) -> float:
        """
        Perform backward propagation on the given output error.
        Computes the dE/dW, dE/dB for a given output_error=dE/dY.
        Returns input_error=dE/dX to feed the previous layer.

        Parameters
        ----------
        output_error: numpy.ndarray
            The output error of the layer.

        Returns
        -------
        float
            The input error of the layer.
        """
        # computes the layer input error (the output error from the previous layer),
        # dE/dX, to pass on to the previous layer
        input_error = np.dot(output_error, self.weights.T)
        # computes the weight error: dE/dW = X.T * dE/dY
        weights_error = np.dot(self.input.T, output_error)
        # computes the bias error: dE/dB = dE/dY
        bias_error = np.sum(output_error, axis=0, keepdims=True)

        # updates parameters
        self.weights = self.w_opt.update(self.weights, weights_error)
        self.biases = self.b_opt.update(self.biases, bias_error)
        return input_error

    def output_shape(self) -> tuple:
        """
        Returns the shape of the output of the layer.

        Returns
        -------
        tuple
            The shape of the output of the layer.
        """
        return (self.n_units,)


class Dropout(Layer):
    """
    Dropout layer of a neural network is a regularization technique where a random set of neurons is
    temporarily ignored dropped out during training, helping prevent overfitting by promoting
    robustness and generalization in the model.

    """

    def __init__(self, rate: float):
        """
        Initialize the dropout layer.

        Parameters
        ----------
        rate: float
            The dropout rate, i.e., the fraction of the input units to drop.
        """
        super().__init__()
        self.rate = rate
        self._input_shape = None

        self.input = None
        self.output = None


    def forward_propagation(self, input: np.ndarray, training: bool) -> np.ndarray:
        """
        Perform forward propagation on the given input.

        Parameters
        ----------
        input: numpy.ndarray
            The input to the layer.
        training: bool
            Whether the layer is in training mode or in inference mode.

        Returns
        -------
        numpy.ndarray
            The output of the layer.
        """
        self.input = input
        if training:
            # Computethe scaling factor (1 / (1-probability))
            self.scale = 1 / (1 - self.rate)

            # Compute the mask using a binomial distribution with probability (1-probability ) and with size equal to the input;
            self.mask = np.random.binomial(1, 1 - self.rate, size=input.shape) / (1 - self.rate)

            # Compute the output (input * mask * scaling factor)
            self.output = input * self.mask * self.scale

            return self.output
        
        if not training:
            self.output = input
            return self.output
        
    
    def backward_propagation(self, output_error: np.ndarray) -> float:
        """
        Performs backward propagation on the given error, i.e., 
        multiplies the received error by the mask

        Parameters
        ----------
        output_error: numpy.ndarray
            The output error of the layer.

        Returns
        -------
        float
            The input error of the layer.
        """
        # multiply the output_error by the mask and return it

        input_error = output_error * self.mask * self.scale

        return input_error
    

    def output_shape(self) -> tuple:
        """
        Returns the input_shape (dropout does not change the shape of the data)

        Returns
        -------
        tuple
            The shape of the output of the layer.
        """
        return self.input_shape()


    def parameters(self) -> int:
        """
        Returns the number of parameters of the layer.

        Returns
        -------
        int
            The number of parameters of the layer.
        """
        return 0
    


if __name__ == '__main__':

    np.random.seed(42)
    
    input_data = np.random.randn(100, 50)
    dropout_layer = Dropout(rate=0.2)

    out_training = dropout_layer.forward_propagation(input_data, training=True)
    out_inference = dropout_layer.forward_propagation(input_data, training=False)

    
  
    import tensorflow as tf
    import keras

    tf_dropout_layer = tf.keras.layers.Dropout(rate=0.2)
    out_training_tf = tf_dropout_layer(input_data, training=True).numpy()
    out_inference_tf = tf_dropout_layer(input_data, training=False).numpy()

    print('Input data:',input_data)
    print('Mask:',dropout_layer.mask)

    print('SI implementation output training:', out_training)
    print('TF output training:', out_training_tf)

    print('SI implementation output inference:', out_inference)
    print('TF output inference:', out_inference_tf)
    
    
    
