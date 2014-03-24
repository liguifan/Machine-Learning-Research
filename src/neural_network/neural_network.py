'''
Module to construct a fully connected neural network.
'''
import argparse
import copy
import cPickle as pickle
import numpy as np
import time

from activation_functions import get_actv_func
from cost_functions import logistic_cost

class network:
    def __init__(self, actv_func):
        self.actv, self.actv_der = get_actv_func(actv_func)

    def __random_weights(self, n_features, n_classes, hidden_units):
        '''
        Initializes weights for 1 hidden layer neural network architecture.
        Weights are chosed uniformly from [-0.5, 0.5).

        Return: theta - weight matrix for the neural network.
        ''' 
        theta = []
        theta.append(np.random.rand(hidden_units, n_features) -
                0.5) 

        col_inds = np.arange(hidden_units).reshape((n_classes,-1),
                order='F').reshape((-1,)) 
        row_inds =np.tile(np.arange(n_classes),(hidden_units/n_classes,
                1)).T.reshape(-1) 
        weights = np.zeros((n_classes, hidden_units))
        weights[row_inds, col_inds] = np.random.rand(hidden_units) - 0.5
        theta.append(weights)

        return theta

    def __get_indicator_vector(self, Y):
        '''
        convert Y into a matrix of indicator vectors
        '''
        n_classes = np.unique(Y).size
        new_Y = np.zeros((Y.size, n_classes), dtype=int)
        new_Y[np.array(range(Y.size)), Y] = 1
        return new_Y

    def __extend_for_bias(self, X):
        '''
        Extend the feature matrix to add bias.
        '''
        X = np.concatenate((np.ones(X.shape[0])[:, np.newaxis], X), axis=1)
        return X

    def __fwd_prop(self, x, theta):
        '''
        Forward propagate the input value with weights theta and return
        activations at each stage. The first activation entry is always the
        input itself.
        '''
        activation = [x]
        # calculate activations at hidden layer and output layers
        for ind, l_wt in enumerate(theta):
            activation.append(self.actv(np.dot(l_wt, activation[ind]))) 
        return activation
             
    def __back_prop(self, activation, y, theta):
        '''
        Calculates final error and back propogate it to all layers. Use
        activations generated by the forward propogation under the current
        weights. 

        Returns errors on all the hidden layers and output layer in that order.
        '''
        n_layers = len(theta) + 1
        errors = [activation[-1] - y]

        # compute errors on hidden layers from o/p to i/p direction
        for ind in range(n_layers - 2):
            layer_ind = -(1 + ind)
            wt = theta[layer_ind]
            act = activation[layer_ind - 1]
            next_layer_err = errors[-1]
            errors.append(np.multiply(np.dot(wt.T, next_layer_err),
                self.actv_der(act))) 
        errors.reverse()
        return errors

    def __derivatives(self, x, y, theta):
        '''
        Calculates the partial derivatives at given x and y using fwd and back
        propagation.

        Return partial derivatives for the weight matrices.
        '''
        activation = self.__fwd_prop(x, theta)
        deltas = self.__back_prop(activation, y, theta)
        p_derivs = [np.outer(deltas[layer], activation[layer]) for layer in
                range(0, len(activation) - 1)] 
        return p_derivs

    def check_gradient(self, X, Y, hidden_units = 100):
        '''
        Checks gradients computed by back propagation.
        
        Return: True/False - True if the gradients computed by back_prop are
                within 0.001 of the numerically computed gradients.
        '''
        X = self.__extend_for_bias(X)
        _, n_features = X.shape
        n_classes = np.unique(Y).size
        Y = self.__get_indicator_vector(Y)
        theta = self.__random_weights(n_features, n_classes, hidden_units)

        # calculate gradient using back propagation
        s = time.time()
        derv = [np.zeros_like(weights) for weights in theta]
        for row in range(X.shape[0]):
            derv_c = self.__derivatives(X[row], Y[row], theta)
            for i in range(len(derv)): derv[i] += derv_c[i]
        print "backprop derivatives computed - ", time.time() - s, "secs" 

        # calculate gradient numerically
        EPS = 10e-4
        grad = [np.empty_like(weights) for weights in theta]
        for layer in range(len(theta)): 
            for (x,y), _ in np.ndenumerate(theta[layer]):
                layer_wts_cp = copy.deepcopy(theta) 
                layer_wts_cp[layer][x][y] += EPS
                cost_1 = logistic_cost(Y, self.predict(X, layer_wts_cp, False))
                layer_wts_cp = copy.deepcopy(theta) 
                layer_wts_cp[layer][x][y] -= EPS
                cost_2 = logistic_cost(Y, self.predict(X, layer_wts_cp, False))
                grad[layer][x][y] = (cost_1 - cost_2) / 2 * EPS 

        diff = [np.amax(np.absolute(gradl - dervl)) for gradl, dervl in
                zip(grad, derv)]
        print max(diff)
        return max(diff) < 0.001

    def __update_weights(self, p_derivs, learning_rate, theta):
        '''
        Updates the current weights using the given partial derivatives and the
        learning rate.
        '''
        for layer in range(len(theta)): 
            theta[layer] -=  p_derivs[layer]

    def __sgd(self, X, Y, theta, epochs = 70000, learning_rate = 1.0):
        '''
        Performs stochastic gradient descent on the dataset X,Y for the given
        number of epochs using the given learning rate.
        '''
        for ind in range(X.shape[0]):
           p_derivs = self.__derivatives(X[ind], Y[ind], theta)
           self.__update_weights(p_derivs, learning_rate, theta)
           if ind % 100 == 0:
               print "Iterations completed: ", ind + 1
        print "Iterations completed: ", ind

    def train(self, X, Y, hidden_units = None, theta = None, add_bias = True):
        '''
        Trains the network using Stochastic Gradient Descent. Initialize the
        network with the weights theta, if provided, else uses the hidden units
        parameter and generates weights theta randomly. Training data is assumed
        to be randomly shuffled already. 

        Return: theta - final weights of the network
        '''
        ok = (hidden_units is not None or theta is not None)
        assert ok, 'hidden units / weights missing'

        if add_bias: X = self.__extend_for_bias(X)
        Y = self.__get_indicator_vector(Y)
        n_examples, n_features = X.shape
        _, n_classes = Y.shape

        # initialize network
        if theta == None:
            theta = self.__random_weights(n_features, n_classes, hidden_units)

        # train
        self.__sgd(X, Y, theta)
        return theta
        
    def predict(self, X, theta, add_bias = True):
        '''
        Predict the activations obtained for all classes under the current
        model.

        Return: acvt - matrix of activations for each example under the weights
                theta.
        '''
        if add_bias: X = self.__extend_for_bias(X)
        r, _ = X.shape
        n_classes, _ = theta[-1].shape
        actv = np.empty([r, n_classes])
        for row in range(r): actv[row, :] = self.__fwd_prop(X[row], theta)[-1]
        return actv

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Check backprop gradient \
            computation by comparing with numerically computed gradient ')
    parser.add_argument('data_file', help = 'data file containing feature and \
            labels')
    args = parser.parse_args()
    nnet = network('logistic')
    data = pickle.load(open(args.data_file)) 
    assert nnet.check_gradient(data['X'], data['Y'], hidden_units = 10), 'Incorrect gradient!'

