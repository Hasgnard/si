from abc import abstractmethod
import unittest
import numpy as np


class Optimizer:

    def __init__(self, learning_rate: float):
        self.learning_rate = learning_rate

    @abstractmethod
    def update(self, w: np.ndarray, grad_loss_w: np.ndarray) -> np.ndarray:
        """
        Update the weights of the layer.

        Parameters
        ----------
        w: numpy.ndarray
            The current weights of the layer.
        grad_loss_w: numpy.ndarray
            The gradient of the loss function with respect to the weights.

        Returns
        -------
        numpy.ndarray
            The updated weights of the layer.
        """
        raise NotImplementedError


class SGD(Optimizer):

    def __init__(self, learning_rate: float = 0.01, momentum: float = 0.0):
        """
        Initialize the optimizer.

        Parameters
        ----------
        learning_rate: float
            The learning rate to use for updating the weights.
        momentum:
            The momentum to use for updating the weights.
        """
        super().__init__(learning_rate)
        self.momentum = momentum
        self.retained_gradient = None

    def update(self, w: np.ndarray, grad_loss_w: np.ndarray) -> np.ndarray:
        """
        Update the weights of the layer.

        Parameters
        ----------
        w: numpy.ndarray
            The current weights of the layer.
        grad_loss_w: numpy.ndarray
            The gradient of the loss function with respect to the weights.

        Returns
        -------
        numpy.ndarray
            The updated weights of the layer.
        """
        if self.retained_gradient is None:
            self.retained_gradient = np.zeros(np.shape(w))
        self.retained_gradient = self.momentum * self.retained_gradient + (1 - self.momentum) * grad_loss_w
        return w - self.learning_rate * self.retained_gradient


class Adam(Optimizer):

    '''
    It uses the squared gradients to scale the learning rate like
    RMSprop and it takes advantage of momentum by using moving average of
    the gradient instead of gradient itself like SGD with momentum.
    '''
    def __init__(self, learning_rate: float = 0.01, beta_1: float = 0.9, beta_2: float = 0.999, epsilon: float = 1e-8):
        """
        Initialize the optimizer.

        Parameters
        ----------
        learning_rate: float
            The learning rate to use for updating the weights.
        beta_1: float
            The beta_1 parameter of the Adam optimizer.
        beta_2: float
            The beta_2 parameter of the Adam optimizer.
        epsilon: float
            The epsilon parameter of the Adam optimizer.
        """
        super().__init__(learning_rate)
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.epsilon = epsilon
        self.m = None
        self.v = None
        self.t = 0

    def update(self, w: np.ndarray, grad_loss_w: np.ndarray) -> np.ndarray:
        """
        Update the weights of the layer.

        Parameters
        ----------
        w: numpy.ndarray
            The current weights of the layer.
        grad_loss_w: numpy.ndarray
            The gradient of the loss function with respect to the weights.

        Returns
        -------
        numpy.ndarray
            The updated weights of the layer.
        """
        # verify if m and v are initialized , if not initialize them as matrices of zeros;
        if self.m is None:
            self.m = np.zeros(np.shape(w))
        if self.v is None:
            self.v = np.zeros(np.shape(w))
        # update the parameters            
        self.t += 1
        self.m = self.beta_1 * self.m + (1 - self.beta_1) * grad_loss_w
        self.v = self.beta_2 * self.v + (1 - self.beta_2) * np.power(grad_loss_w, 2)
        m_hat = self.m / (1 - np.power(self.beta_1, self.t))
        v_hat = self.v / (1 - np.power(self.beta_2, self.t))
        return w - self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)
    