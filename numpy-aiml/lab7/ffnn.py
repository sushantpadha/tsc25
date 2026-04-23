import numpy as np

# TODO: Hurt your head by writing backprop from scratch!
class FeedForwardNN:

    def __init__(self, layer_sizes, hidden_activation='relu', output_activation='sigmoid', learning_rate=0.01):
        self.layer_sizes = layer_sizes
        self.hidden_act = hidden_activation
        self.output_act = output_activation
        self.learning_rate = learning_rate

        self.L = len(layer_sizes) - 1
        self.weights = []
        self.biases = []

        self.pre_activations = []
        self.activations = []

        self.initialize_parameters()


    def initialize_parameters(self):
        """
        Initialize all the parameters of the neural network.
        All the weights with appropriate shapes
        Do random initialization using standard normal distribution
        and all the biases.
        For weigths initialize them with a scale of  2 / sqrt(in) (To mantain variance)
        """

        # DO NOT REMOVE
        np.random.seed(42)

        # code for initializing values; given to you :D
        for l in range(self.L):
            din = self.layer_sizes[l]
            dout = self.layer_sizes[l+1]
            W = np.random.randn(din, dout) * np.sqrt(2.0 / din)
            # b = np.clip(np.random.randn(1, dout) * 0.1, 0, 0.1)
            # b = np.clip(np.random.randn(1, dout) * 0.1, -0.1, 0)
            b = np.random.randn(1, dout) * 0.1
            # b = np.zeros((1, dout))
            self.weights.append(W)
            self.biases.append(b)


    def relu(self, z: np.ndarray):
        """
        Implement reLu on z
        z: np.ndarray
        output: np.ndarray with relu applied to it (Same shape as z)
        """

        return np.maximum(0,z)


    def relu_derivative(self, z: np.ndarray):
        """
        Implement the derivative of relu on z
        z: np.ndarray
        output: np.ndarray with relu's derivative (Same shape as z)
        """
        return (z > 0).astype(float)


    def sigmoid(self, z: np.ndarray):
        """
        Implement sigmoid on z
        z: np.ndarray
        output: np.ndarray with sigmoid applied to it (Same shape as z)
        don't forget to clip
        """

        return 1.0 / (1.0 + np.exp(np.clip(-z, -300, 300)))


    def sigmoid_derivative(self, z: np.ndarray):
        """
        Implement sigmoid derivative on z
        z: np.ndarray
        output: np.ndarray with sigmoid derivative applied to it (Same shape as z)
        don't forget to clip
        """

        s = self.sigmoid(z)
        return s * (1-s)


    def softmax(self, z: np.ndarray):
        """
        Implement softmax on Z: np.ndarray (N, d)
        Output: np.ndarray with softmax taken on each row (N, d)
        don't forget to make it numerically stable
        """
        z_c = z - np.max(z, axis=1, keepdims=True)
        expZ = np.exp(z_c)
        return expZ / np.sum(expZ, axis=1, keepdims=True)


    def activate(self, z: np.ndarray, activation_type: str):
        """
        Handle the correct activation function for z.

        Return the value of applying said activation function to z

        """
        if activation_type == 'relu':
            return self.relu(z)
        elif activation_type == 'sigmoid':
            return self.sigmoid(z)
        elif activation_type == 'softmax':
            return self.softmax(z)
        else:
            return z


    def forward_propagation(self, X: np.ndarray):
        """
        Implement Forward propogation.

        Fill in the activations and pre-activations arrays appropriately. 

        return the final output of the neural net (after the output layer activation)

        """
        self.pre_activations = []  # length = L
        self.activations = [X]     # length = L+1

        # TODO: Implement forward prop!
        # Remember the invariant: z_l = a_l @ W_l + b_l   -->  a_{l+1} = f ( z_l )
        # Here, treat l=0,..L-1 as index into the lists above
        # Activations always have batch size (B) as leading dimension!
        
        # Try to append to the above lists as you keep proceeding
        
        # ? Why do we need to store the full list? Backprop will answer that
        
        for l in range(self.L):
            pass # TODO

        return self.activations[-1].copy() # a hint? :P


    def backward_propagation(self, grads: np.ndarray):
        """
        Implement backward propogation

        grads is the gradient of the loss with respect to the output of the final layer. (It is slightly different in semantics from delta so keep that in mind)

        propogate the grad_weights and grad_biases arrays appropriately

        return grad_weights, grad_biases

        """

        grad_weights = [np.zeros_like(w) for w in self.weights]
        grad_biases  = [np.zeros_like(b) for b in self.biases]
        
        if len(self.pre_activations) == 0 or len(self.activations) == 0:
            raise Exception("Run forward propogation first")
        
        # TODO: Here are some hints/invariants to maintain while computing
        # grads entering this function = dL/da : shape=(N, layer_sizes[-1])
        # delta                        = dL/dz
        # delta = grads * act'(z)   (except softmax which couples all coords)
        #
        # per layer we need:
        #   dW[l] = a_prev.T @ delta        shape: (layer_sizes[l], layer_sizes[l+1])
        #   db[l] = sum(delta, axis=0)      shape: (1, layer_sizes[l+1])
        #   grads for next iter = delta @ W[l].T   shape: (N, layer_sizes[l])
        
        # i liek dispatch tables :D
        # ! a utility to directly compute the multiplicative effect of the derivative of activation(z)
        # ! on computed "delta" (remember delta represented dL/dz, grads wrt to pre-activations)
        self._act_derivative = {
            'relu':    lambda z, s, g: g * self.relu_derivative(z),
            'sigmoid': lambda z, s, g: g * self.sigmoid_derivative(z),
            'linear':  lambda z, s, g: g,
            'softmax': lambda z, s, g: s * (g - np.sum(g * s, axis=1, keepdims=True)),
        }

        for l in reversed(range(self.L)):
            # eg: layer_sizes = [1, 10,    8, 1]
            #                    0  1 ... L-1 L (indices)
            # L = 3
            # we iterate over l = 2, 1, 0
            # activations = [(N,1), (N,10), (N ,8), (N,1)]
            # preactivans =        [(N,10), (N ,8), (N,1)]
            # weights     =        [(1,10), (10,8), (8,1)]
            #
            # delta shape = (N, layer_sizes[l+1])
            
            z      = None  # TODO shape: (N, layer_sizes[l+1])
            a_prev = None  # TODO shape: (N, layer_sizes[l])
            
            # convert grads to delta
            act = self.hidden_act if l < self.L-1 else self.output_act
            # magic of dict
            delta = None # TODO: compute delta
            
            grad_weights[l] += None # TODO: (layer_sizes[l], layer_sizes[l+1])
            grad_biases[l]  += None # TODO: (1, layer_sizes[l+1])
            
            grads = None # TODO: (N, layer_sizes[l])

        return grad_weights, grad_biases




    def update_parameters(self, grad_weights: list, grad_biases: list):
        """
        Update all the paramters according to grad_weights and grad_biases (with learning rate)

        """
        for l in range(self.L):
            self.weights[l] -= self.learning_rate * grad_weights[l]
            self.biases[l]  -= self.learning_rate * grad_biases[l]

    def train(self, X: np.ndarray, y: np.ndarray, epochs=10000):
        """
        Train the neural network. For now no need to implement any batching etc. In each epoch run forward backward and update on the whole dataset.
        Assume that we will only do regression with MSE loss.
        """
        for epoch in range(epochs):
            y_hat = self.forward_propagation(X)       # (N, 1)
            grads = (y_hat - y) / len(y)              # (N, 1)
            grad_w, grad_b = self.backward_propagation(grads)
            self.update_parameters(grad_w, grad_b)

            if epoch % 1000 == 0:
                loss = np.mean((y_hat - y) ** 2) / 2
                print(f"Epoch {epoch} Loss {loss}")