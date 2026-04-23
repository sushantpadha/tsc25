import numpy as np
from ffnn import FeedForwardNN


class MoE:

    def __init__(self, input_dim, hidden_dim, num_experts, expert_layers, learning_rate=0.01, router_reg=0.01):

        self.num_experts = num_experts
        self.learning_rate = learning_rate
        self.router_reg = router_reg

        # Router network
        self.router = FeedForwardNN(
            layer_sizes=[input_dim, hidden_dim, num_experts],
            hidden_activation='relu',
            output_activation='softmax',
            learning_rate=learning_rate
        )

        # Experts
        self.experts = [
            FeedForwardNN(
                layer_sizes=expert_layers,
                hidden_activation='relu',
                output_activation='linear',
                learning_rate=learning_rate
            )
            for _ in range(num_experts)
        ]
        self.gates = None
        self.expert_outputs = None
        
        # adding to break symmetry!
        # ! is this allowed?
        # for i, expert in enumerate(self.experts):
        #     for w in expert.weights:
        #         w += np.random.randn(*w.shape) * 0.1 * i


    def forward(self, X: np.ndarray):
        """
        Run forward passes on all the models

        populate self.gates (N, K) and self.expert_outputs (N, K, D)
        here N = number of rows in data
             K = number of experts
             D = number of columns in data -- dimension in which expert outputs, usually has size 1


        return the final prediction of the model

        """
        # what's written above doesn't make sense :/
        
        self.gates = self.router.forward_propagation(X)

        # ! assuming that expert_outputs is (N, K, layer_sizes[-1])
        self.expert_outputs = np.zeros((X.shape[0], self.num_experts, self.experts[0].layer_sizes[-1]))
        
        for i in range(self.num_experts):
            self.expert_outputs[:, i, :] = self.experts[i].forward_propagation(X)

        return np.sum(self.gates[:, :, None] * self.expert_outputs, axis=1)  # (N,D)

    def backward(self, grad_output: np.ndarray):
        """
        For each model calculate the gradient of the loss with respect to the model outputs.
        Add regularization in the case of the router (router_grad -= self.router_reg * entropy_grad)

        Run backward propogation on each model.

        After that update the paramters of each model as well. (We will not have a seperate update parameters function like the ffnn)


        """
        # loss = MSE - lam * H(g(x)) = MSE + lam * sum{ g(x) .* log(g(x)) }
        # dL/dg = (y - y_hat) * f(x) / N  + (1+log(g(x)))
        
        if self.gates is None or self.expert_outputs is None:
            raise Exception("Run forward propogation first")
                
        ## expert grads
        # dL/df_k = grad_output * g_k(x)  shape=(N,D)*(N,1)
        for k in range(self.num_experts):
            # TODO: call backprop suitably on each expert, and take 1 grad descent step
            
        ## router grads
        # dL/dg = grad_output * f(x) + lam*(1+log(g(x)))  shape=(N,1,D)*(N,K,D).sum(axis=2) + (N,K)
        # i want to get shape = (N, K) -- (Num inputs, Num experts)
        mse_grad = None # ! TODO: Compute gradient of MSE wrt output first
        entropy_grad = None # ! TODO: Compute gradient of entropy wrt output - N,K
        
        router_grad = mse_grad - entropy_grad / (grad_output.shape[0])
        
        assert router_grad.shape == (grad_output.shape[0], self.num_experts)
                
        grads = self.router.backward_propagation(router_grad)
        self.router.update_parameters(*grads)
        
        return mse_grad, entropy_grad


    def loss_grad(self, y_pred: np.ndarray, y: np.ndarray):
        """
        Return how the loss changes with the output of the model. (Ignore the regularization term here).

        """

        return (y_pred-y) / y.shape[0] # shape = (N,D)


    def train(self, X: np.ndarray, y: np.ndarray, epochs=1000, print_freq=1000):

        for epoch in range(epochs):

            y_pred = self.forward(X)


            grad_output = self.loss_grad(y_pred, y)

            g = self.backward(grad_output)

            if epoch % print_freq == 0:
                #TODO fill in appropriate loss function here. (You may want to use the same loss for both ffnn and moe to better be able to compare them
                # This need not be the same as the training loss
                if self.gates is None:
                    raise Exception("Run forward propogation first")
                loss = np.mean((y_pred - y) ** 2, axis=(0,1)) / 2  # ! this is a scalar
                # regloss = - self.router_reg * np.sum(self.gates * np.log(self.gates + 1e-10))
                # print(f"Epoch {epoch} | Loss {loss:.6f} | Reg term: {regloss:.6f}")
                print(f"Epoch {epoch} | Loss {loss:.6f}")
                
                # print(self.gates[4])
                # print("MSE term:", np.linalg.norm(g[0]))
                # print("Reg term:", np.linalg.norm(g[1]))
                
                
