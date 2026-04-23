"""
q4.py
=====
Task: Implement multi-class generative classifiers trained using

(1) Exact Normalization (Softmax)
(2) Importance Sampling (IS)
(3) Noise Contrastive Estimation (NCE)

Training is performed using mini-batch gradient descent
with on-the-fly sampling where required.

You are expected to fill in the TODOs only.
Do NOT change function signatures.
"""

import numpy as np


# ======================================================
# METRICS
# ======================================================

def accuracy(y_true, y_pred):
    """
    Compute overall classification accuracy.

    Args:
        y_true (np.ndarray): True labels, shape (N,)
        y_pred (np.ndarray): Predicted labels, shape (N,)

    Returns:
        float
    """
    return (y_pred==y_true).mean().item()


def precision(y_true, y_pred, cls):
    """
    Precision for class cls (one-vs-rest).

    Args:
        y_true (np.ndarray): shape (N,)
        y_pred (np.ndarray): shape (N,)
        cls (int)

    Returns:
        float
    """
    tp = ((y_true == cls) & (y_pred == cls)).sum().item()
    fp = ((y_true != cls) & (y_pred == cls)).sum().item()
    return tp / (tp + fp) if ((tp+fp )> 0) else 0


def recall(y_true, y_pred, cls):
    """
    Recall for class cls (one-vs-rest).

    Args:
        y_true (np.ndarray): shape (N,)
        y_pred (np.ndarray): shape (N,)
        cls (int)

    Returns:
        float
    """
    tp = ((y_true == cls) & (y_pred == cls)).sum().item()
    fn = ((y_true == cls) & (y_pred != cls)).sum().item()
    return tp / (tp + fn) if ((tp+fn) > 0) else 0


def f1_score(y_true, y_pred, cls):
    """
    F1 score for class cls.

    Args:
        y_true (np.ndarray): shape (N,)
        y_pred (np.ndarray): shape (N,)
        cls (int)

    Returns:
        float
    """
    pr = precision(y_true, y_pred, cls)
    re = recall(y_true, y_pred, cls)
    return 2*pr*re/(pr + re) if ((pr+re)>0) else 0

# ======================================================
# COMMON UTILITIES
# ======================================================

def sigmoid(z):
    """
    Sigmoid nonlinearity (used in NCE).

    Args:
        z (np.ndarray)

    Returns:
        np.ndarray: same shape as z, values in (0,1)
    """
    return 1 / (1 + np.exp(np.clip(-z, -500, 500)))


def softmax(scores):
    """
    Numerically stable softmax (row-wise).

    Args:
        scores (np.ndarray): shape (B, K)

    Returns:
        np.ndarray: probabilities, shape (B, K)
    """
    maxs = scores.max(axis=1, keepdims=True)
    sc_e = np.exp(np.clip(scores-maxs, -500, 500))
    sums = sc_e.sum(axis=1, keepdims=True)
    return sc_e / sums


# ======================================================
# GENERIC SAMPLER INTERFACE
# ======================================================

class Sampler:
    """
    Generic sampler interface.

    Students are encouraged to subclass this class to implement
    any proposal or noise distribution they want.
    """

    def sample(self, num_samples):
        """
        Draw samples from q.

        Args:
            num_samples (int)

        Returns:
            np.ndarray
        """
        raise NotImplementedError

    def prob(self, samples):
        """
        Evaluate q(samples).

        Args:
            samples (np.ndarray)

        Returns:
            np.ndarray: densities, shape (num_samples,)
        """
        raise NotImplementedError


class GaussianSampler(Sampler):

    def __init__(self, mean, cov):
        self.mean = mean
        self.cov = cov

        self.D = mean.shape[0]

        # Precompute for density evaluation
        self.cov_inv = np.linalg.inv(cov)
        sign, logdet = np.linalg.slogdet(cov)
        if sign <= 0:
            raise ValueError("Covariance must be positive definite.")
        self.log_det = logdet

        self.norm_const = -0.5 * (self.D * np.log(2 * np.pi) + self.log_det)

    def sample(self, num_samples):
        return np.random.multivariate_normal(
            mean=self.mean,
            cov=self.cov,
            size=num_samples
        )

    def prob(self, samples):
        """
        Returns density values (not log-density).
        """
        diff = samples - self.mean              # (N, D)
        quad = np.sum((diff @ self.cov_inv) * diff, axis=1)  # (N,)
        log_density = self.norm_const - 0.5 * quad
        return np.exp(log_density)


class CategoricalSampler(Sampler):

    def __init__(self, probs):
        self.probs = probs / probs.sum()
        self.K = len(self.probs)

    def sample(self, num_samples):
        return np.random.choice(
            self.K,
            size=num_samples,
            p=self.probs
        )

    def prob(self, samples):
        return self.probs[samples]

# ======================================================
# SOFTMAX GENERATIVE CLASSIFIER (EXACT NORMALIZATION)
# ======================================================

class SoftmaxGenerativeClassifier:
    """
    Multi-class generative classifier trained using
    exact normalization (softmax).
    """

    def __init__(self, num_classes, lr=1e-2,
                 batch_size=64, max_epochs=1000):
        """
        Args:
            num_classes (int): K
            lr (float)
            batch_size (int)
            max_epochs (int)
        """
        self.K = num_classes
        self.lr = lr
        self.batch_size = batch_size # also referred to as B in a lot of places
        self.max_epochs = max_epochs

        # Discriminative parameters
        self.W = None  # shape (K, D)
        self.b = None  # shape (K,)

        # Recovered generative parameters
        self.mu = None     # shape (K, D)
        self.Sigma = None # shape (D, D)
        self.pi = None    # shape (K,)

    def score(self, X):
        """
        Compute unnormalized scores p(x,y).

        Args:
            X (np.ndarray): shape (B, D)

        Returns:
            np.ndarray: shape (B, K)
        """
        z = (X @ self.W.T + self.b[None, :])
        return np.exp(np.clip(z, -500, 500))

    def gradients(self, X, y):
        """
        Gradients of conditional log-likelihood.

        Args:
            X (np.ndarray): shape (B, D)
            y (np.ndarray): shape (B,)

        Returns:
            tuple W,b
                'W': np.ndarray, shape (K, D)
                'b': np.ndarray, shape (K,)
        """
        B,D = X.shape
        
        z = (X @ self.W.T + self.b)  # B,K
        prob = softmax(z) / B
        
        y_oh = np.eye(self.K)[y] / B # B K
        
        grad_w = (prob - y_oh).T @ X
        grad_b = (prob - y_oh).sum(axis=0).flatten()
        
        assert(grad_w.shape[0] == self.K)
        assert(grad_w.shape[1] == D)
        assert(grad_b.shape[0] == self.K)
        
        return grad_w, grad_b

    def fit(self, X, y):
        """
        Train using mini-batch gradient descent.

        Args:
            X (np.ndarray): shape (N, D)
            y (np.ndarray): shape (N,)
        """
        B = self.batch_size
        N, D = X.shape
        lr = self.lr
        
        idxs = np.arange(N)
        np.random.shuffle(idxs)
        cur  = 0
        
        self.W = np.zeros((self.K,D))
        self.b = np.zeros((self.K,))
        # print(self.K)
        
        for i in range(self.max_epochs):
            ind = idxs[cur:cur+B]
            cur+=B
            if cur+B > N:
                cur=0
                np.random.shuffle(idxs)
                
            X_b, y_b = X[ind], y[ind]
            gw, gb = self.gradients(X_b, y_b)
            
            if i%10000 == 0:
                # print(f"{i}:\t |gw|={np.linalg.norm(gw):.5f}\t |gb|={np.linalg.norm(gb):.5f}")
                pass
            
            self.W -= lr * gw
            self.b -= lr * gb
        
        # self.W = W
        # self.b = b
            
    def predict_proba(self, X):
        """
        Compute p(y|x) using exact softmax.

        Args:
            X (np.ndarray): shape (N, D)

        Returns:
            np.ndarray: shape (N, K)
        """
        z = (X @ self.W.T + self.b)  # N,K
        return softmax(z)  

    def predict(self, X):
        """
        Returns the actual prediction on the basis of predicted probabilities

        Args:
            X (np.ndarray): shape (N, D)

        Returns:
            np.ndarray: shape (N,)
        """
        prob = self.predict_proba(X)
        return prob.argmax(axis=1).flatten()

    def recover_parameters(self):
        """
        Recover Gaussian parameters from trained W and b.


        Stores the parameters pi_k and Sigma into the class variables, note that self.mu
        will be populated by the main code by this point, so assume that self.mu contains the correct value
        """
        # self.mu is good
        D = self.W.shape[1]
        self.mu = self.empirical_mu
        # print(self.W.shape, self.mu.shape)
        
        Sigma_inv = np.linalg.pinv(self.mu) @ self.W
        self.Sigma = np.linalg.pinv(Sigma_inv)
        # print(self.Sigma.shape, self.mu.shape)
        
        self.pi = np.exp( self.b + (0.5) * ((self.mu @ Sigma_inv) * self.mu).sum(axis=1).flatten() )
        summ = self.pi.sum()
        self.pi /= summ

# ======================================================
# IMPORTANCE SAMPLING CLASSIFIER
# ======================================================

class ImportanceSamplingClassifier:
    """
    Multi-class generative classifier trained using
    importance sampling to approximate normalization.
    """

    def __init__(self, num_classes, lr=1e-3,
                 batch_size=40, num_samples=128, max_epochs=23,
                 class_sampler=None):
        """
        Args:
            num_classes (int)
            lr (float)
            batch_size (int)
            num_samples (int): M
            max_epochs (int)
            class_sampler (Sampler): q(y)
        """
        self.K = num_classes
        self.lr = lr
        self.batch_size = batch_size
        self.M = num_samples
        self.max_epochs = max_epochs
        self.class_sampler: Sampler = class_sampler

        self.W = None  # shape (K, D)
        self.b = None  # shape (K,)
        self.loss_history = []

    def score(self, X):
        """
        Args:
            X (np.ndarray): shape (B, D)

        Returns:
            np.ndarray: shape (B, K)
        """
        logits = X @ self.W.T + self.b  # (B, K)
        logits = np.clip(logits, -500, 500)  # numerical stability
        return np.exp(logits)

    def estimate_normalizer(self, X):
        """
        Importance-sampled estimate of Z(x). Note that you should reuse the samples of y obtained for 1 batch
        Only draw new samples when you move to the next batch in training

        Args:
            X (np.ndarray): shape (B, D)

        Returns:
            np.ndarray: shape (B,)
        """
        self.y_m  = self.class_sampler.sample(self.M)
        q_m  = self.class_sampler.prob(self.y_m)
        
        logits         = X @ self.W[self.y_m].T + self.b[self.y_m]
        sampled_scores = np.exp(np.clip( logits, -500, 500 ))
        
        # scores = self.score(X)
        # sampled_scores = scores[:, self.y_m]
        
        weights = sampled_scores / q_m[None, :]
        ans     = weights.mean(axis=1).flatten()
        assert(ans.shape[0] == X.shape[0])
        return ans
    
        # pi_m = self.priors[y_m]
        # oh = np.eye(self.K)[y_m]  # M K
        # probs = (scores @ oh.T)  # B M
        # probs_b = (probs * (pi_m / q_m)[None, :])  # B M
        # return probs_b.mean(axis=1).flatten()
        
    def gradients(self, X, y):
        B, D = X.shape
        z_hat = self.estimate_normalizer(X)
        q_m   = self.class_sampler.prob(self.y_m)
        
        sampled_logits = X @ self.W[self.y_m].T + self.b[self.y_m]
        sampled_scores = np.exp( np.clip( sampled_logits, -600, 600) )
        
        P_sampled = sampled_scores / (self.M * q_m[None, :] * z_hat[:, None])
        
        error = np.zeros((B,self.K))
        
        np.add.at(error, (slice(None), self.y_m), P_sampled)
        
        error[np.arange(B), y] -= 1
        
        grad_w = (error.T @ X) / B
        grad_b = np.mean(error, axis=0)
        
        return grad_w, grad_b


    def fit(self, X, y):
        N, D = X.shape
            
        if self.W is None:
            self.W = np.random.randn(self.K, D) / np.sqrt(D)
            self.b = np.zeros((self.K,))

        idx = np.arange(N)
        for epoch in range(self.max_epochs):
            np.random.shuffle(idx)
            for i in range(0, N, self.batch_size):
                batch_idx = idx[i:i + self.batch_size]
                X_batch, y_batch = X[batch_idx], y[batch_idx]
                
                grad_w, grad_b = self.gradients(X_batch, y_batch)
                
                self.W -= self.lr * grad_w
                self.b -= self.lr * grad_b
                
            unnorm_scores = self.score(X)[np.arange(X.shape[0]), y]
            z_hat = self.estimate_normalizer(X)
            batch_loss = -np.mean(np.log(unnorm_scores / (z_hat + 1e-10)))
            self.loss_history.append(batch_loss)
                
            if (epoch%2 == 0):
                # print loss
                print(f"{epoch} {accuracy(y, self.predict(X))}")
                

    def predict_proba(self, X):
        """
        Args:
            X (np.ndarray): shape (N, D)

        Returns:
            np.ndarray: shape (N, K)
        """
        score = self.score(X)
        return score / score.sum(axis=1, keepdims=True)

    def predict(self, X):
        """
        Returns the actual prediction on the basis of predicted probabilities

        Args:
            X (np.ndarray): shape (N, D)

        Returns:
            np.ndarray: shape (N,)
        """
        prob = self.predict_proba(X)
        return prob.argmax(axis=1).flatten()

# ======================================================
# NOISE CONTRASTIVE ESTIMATION CLASSIFIER
# ======================================================

class NCEClassifier:
    """
    Multi-class generative classifier trained using
    Noise Contrastive Estimation.
    """

    def __init__(self, num_classes, lr=2e-2,
                 batch_size=40, noise_ratio=11, max_epochs=50,
                 x_sampler=None, y_sampler=None):
        """
        Args:
            num_classes (int)
            lr (float)
            batch_size (int)
            noise_ratio (int): k
            max_epochs (int)
            x_sampler (Sampler): q(x)
            y_sampler (Sampler): q(y)
        """
        self.K = num_classes
        self.lr = lr
        self.batch_size = batch_size
        self.k = noise_ratio
        self.max_epochs = max_epochs
        self.x_sampler: Sampler = x_sampler
        self.y_sampler: Sampler = y_sampler

        self.W = None  # shape (K, D)
        self.b = None  # shape (K,)
        self.c = None  # scalar

    def score(self, X, y):
        """
        Compute p(x,y).

        Args:
            X (np.ndarray): shape (B, D)
            y (np.ndarray): shape (B,)

        Returns:
            np.ndarray: shape (B,)
        """
        if self.W is None or self.b is None:
            raise ValueError("Model not trained yet.")
        
        W_y, b_y = self.W[y], self.b[y]  # B,D
        return (X * W_y).sum(axis=1).flatten() + b_y  # B,D

    def sample_noise(self, num_samples):
        """
        Sample noise pairs from q(x,y).

        Args:
            num_samples (int)

        Returns:
            tuple:
                X_noise (np.ndarray): shape (num_samples, D)
                y_noise (np.ndarray): shape (num_samples,)
        """
        X_noise = self.x_sampler.sample(num_samples)
        y_noise = self.y_sampler.sample(num_samples)
        return X_noise, y_noise

    def gradients(self, X, y):
        """
        Gradients of NCE objective.

        Args:
            X (np.ndarray): shape (B, D)
            y (np.ndarray): shape (B,)

        Returns:
            grad_W, grad_b, grad_c
                'grad_W': np.ndarray, shape (K, D)
                'grad_b': np.ndarray, shape (K,)
                'grad_c': float
        """
        def sigmoid(z): return 1 / (1 + np.exp(np.clip(-z, -500, 500)))
        
        f_th = self.score(X, y)  # B
        X_noise, y_noise = self.sample_noise(self.batch_size * self.k)  # (Bk, D), (Bk,)
        f_th_noise = self.score(X_noise, y_noise)  # Bk
        
        prob_x, prob_y = self.x_sampler.prob(X), self.y_sampler.prob(y) # B, B
        prob_x_noise, prob_y_noise = self.x_sampler.prob(X_noise), self.y_sampler.prob(y_noise) # Bk, Bk
        
        log_kq_real = np.log(self.k) + np.log(prob_x) + np.log(prob_y)
        log_kq_noise = np.log(self.k) + np.log(prob_x_noise) + np.log(prob_y_noise)
        
        # BC logits: f - c - log(kq) 
        z_real = f_th - self.c - log_kq_real # B
        z_noise = f_th_noise - self.c - log_kq_noise # Bk
        
        # p(D=1|sample)
        p_real = sigmoid(z_real) # B
        p_noise = sigmoid(z_noise) # Bk
        
        ## GRAD
        B, D = X.shape
        
        X_all = np.vstack([X, X_noise]) # (B + Bk, D)
        y_all = np.concatenate([y, y_noise]) # (B + Bk,)
        weights = np.concatenate([p_real - 1, p_noise]) # (B + Bk,)
        
        g_w = np.zeros((self.K, D))  # (K, D)
        g_b = np.zeros(self.K)       # (K,)
        
        # gradient accumulation at indices coming from y_all, of weights or weights * X
        np.add.at(g_w, y_all, weights[:, None] * X_all)
        np.add.at(g_b, y_all, weights)
        
        g_c = (np.sum(1 - p_real) - np.sum(p_noise))
        
        return g_w / B, g_b / B, g_c / B

    def fit(self, X, y):
        """
        Train using mini-batch gradient descent.

        Args:
            X (np.ndarray): shape (N, D)
            y (np.ndarray): shape (N,)
        """
        lr = self.lr
        N, D = X.shape
        
        if self.W is None:
            self.W = np.random.randn(self.K, D) / np.sqrt(D)
            self.b = np.zeros((self.K,))
            self.c = 0
        
        for i in range(self.max_epochs):
            idx = np.random.permutation(N)
            for b in range(0, N, self.batch_size):
                ind = idx[b:b+self.batch_size]
                X_b, y_b = X[ind], y[ind]
                gw, gb, gc = self.gradients(X_b, y_b)
                self.W -= lr * gw
                self.b -= lr * gb
                self.c -= lr * gc
            if (i%5 == 0):
                # print loss
                print(f"{i} {accuracy(y, self.predict(X))}")

    def predict_proba(self, X):
        """
        Args:
            X (np.ndarray): shape (N, D)

        Returns:
            np.ndarray: shape (N, K)
        """
        sc = X @ self.W.T + self.b[None, :] # - self.c  # (N, K)
        return softmax(sc)

    def predict(self, X):
        """
        Returns the actual prediction on the basis of predicted probabilities

        Args:
            X (np.ndarray): shape (N, D)

        Returns:
            np.ndarray: shape (N,)
        """
        return self.predict_proba(X).argmax(axis=1).flatten()
