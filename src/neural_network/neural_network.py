'''
Module to construct a fully connected neural network.
'''
import numpy as np
from activation_functions import get_actv_func

class network:
    def __init__(self, layer_units, actv_func):
        self.layer_units = layer_units
        self.layer_weights = None
        self.actv, self.actv_der = get_actv_func(actv_func)

    def __random_init(self, num_features):
        '''
        Randomly initialize the weights of neural network betwee [-0.5, 0.5).
        '''
        inputs = num_features
        for layer in range(1, len(layer_units)): 
            self.layer_weights.append(np.random.rand(inputs,
                self.layer_units[layer]) - 0.5) 
            inputs = self.layer_units[layer]

    def __check_network(self, X, Y):
        '''
        Validate the newtork architecture and the inputs layer_weights, X and Y
        for compatibility.
        '''
        allok = True
        allok = len(self.layer_units) - 1 == len(self.layer_weights)

        # check every layer for consistent weights
        input_units = X.shape[1]
        for layer in range(1, len(self.layer_units)):
            layer_r, layer_c = self.layer_weights[layer - 1].shape
            allok = (self.layer_units[layer] == layer_r and layer_c ==
                    input_units) 
            if not allok break
            input_units = self.layer_units[layer]
        return allok

    def __weights_init(self, layer_weights):
        '''
        Initialize the weights of the neural network with the given weights.
        '''
        self.layer_weights = layer_weights

    def __fwd_prop(self, x):
        '''
        Forward propagate the input value with current weights and return
        activations at each stage.
        '''
        activation = [x]
        for layer in range(1, len(self.layer_units) - 1):
            activation.append(self.actv(np.dot(activation[layer - 1],
                self.layer_weights[layer])))
        return activation
             
    def __back_prop(self, activation, y):
        '''
        Calculate final error and back propogate it to all layers. Use
        activations generated by the forward propogation under the curren
        weights. 
        '''
        error = activation[-1] - y
        deltas = [error] 
        for layer in range(-2, 0, -1):
            jdeltas.append(np.multiply(np.dot(self.layer_weight[layer],
                deltas[-1]), self.actv_der(activation[layer])))
        delta = reverse(delta)

    def __derivatives(self, x, y):
        '''
        Calculates the partial derivatives at given x and y using fwd and back
        propagation.
        '''
        activation = self.fwd_prop(x)
        deltas = self.back_prop(activation, y)
        p_derivs = []
        for layer in range(1, len(activation)):
            p_derivs.append(np.dot(activation[layer], deltas[layer -1]))
        return p_derivs

    def __update_weights(self, p__derivs, learning_rate):
        '''
        Updates the current weights using the given partial derivatives and the
        learning rate.
        '''
        for layer in range(len(self.layer_weights)): 
            self.layer_weights -= np.multiply(learning_rate, p_derivs[layer])

    def __sgd(self, X, Y, epochs = 70000, learning_rate = 1.0):
        '''
        Performs stochastic gradient descent on the dataset X,Y for the given
        number of epochs using the given learning rate.
        '''
        for epoch in range(epochs):
           ind = numpy.random.randint(0, high=70000)
           p_derivs = self.__derivatives(X[ind], Y[ind])
           self.__update_weights(p_derivs, learning_rate)

    def train(self, X, Y, layer_weights = None):
        '''
        Trains the network using Stochastic Gradient Descent. Initialize the
        network with the provided layer_weights. If no layer_weights are
        provided use random weights to initialize the network.
        '''
        if layer_weights == None:self.__random__init(X.shape[1])
        else: self.__weights_init(layer_weights)
        assert self.__check_network(X, Y), 'weights or X,Y incompatible with the \
            network architecture'
        self.__sgd(X,Y)
        
    def save_model(self, ddir, suffix = ''):
        '''
        Save the current model to disk in the ddir directory. Additionally add
        any suffix given to the file name; this can be use to give specific
        names to model based on the settings used to create it.
        '''
        pickle.dump(self.layer_weights, open(path.join(ddir, '_', suffix,
            '.model', 'wb')))
            
    def load_model(self, model_file):
        '''
        Load a saved model.
        '''
        self.layer_weights = pickle.load(open(mode_File))

    def predict(self, X):
        '''
        Predict the classes based on the learned model and measure accuracy. 
        '''
        pred_y = np.empty(Y.shape, dtype=int)
        r, _ = X.shape
        for row in range(r):
            activations = self.__fwd_prop(X[row])[-1]
            pred_y[row] = np.argmax(activations)
        return pred_y
        print np.sum(pred_y == Y) * 1.0 / r
        
        
