import numpy as np
import pandas as pd

class KNN:
    def __init__(self, k=5):
        self.k = k
        self.X_train = None
        self.y_train = None


    def fit(self, X, y):
        """
        Store the training data and labels.
        Parameters:
            X: Training features (numpy array)
            y: Training labels (numpy array)
        """
        self.X_train = X
        self.y_train = y


    def predict_L2(self, X_test, k):
        """
        Predict labels for the test set using L2 (Euclidean) distance.
        Parameters:
            X_test: Test features (numpy array)
            k: Number of neighbors
        Returns:
            y_pred: Predicted labels for X_test (numpy array of +1 or -1)
        """
        # TODO: Implement vectorized L2 distance and majority vote
        return None


    def predict_L1(self, X_test, k):
        """
        Predict labels for the test set using L1 (Manhattan) distance.
        Parameters:
            X_test: Test features (numpy array)
            k: Number of neighbors
        Returns:
            y_pred: Predicted labels for X_test (numpy array of +1 or -1)
        """
        # TODO: Implement vectorized L1 distance and majority vote
        return None

def compute_accuracy(y_true, y_pred):
    """
    Calculate the percentage of correct predictions.
    Parameters:
        y_true: Ground truth labels
        y_pred: Predicted labels
    Returns:
        accuracy: Float representing accuracy
    """
    # TODO
    return None

def standardize(X_train, X_test):
    """
    Standardize features to mean 0 and variance 1.
    Parameters:
        X_train: Raw training features
        X_test: Raw test features
    Returns:
        X_train_std, X_test_std: Standardized feature arrays
    """
    # TODO
    return None

def get_pearson_indices(X, y, m):
    """
    Select top m features based on absolute Pearson correlation with label y.
    Parameters:
        X: Feature array
        y: Label array
        m: Number of features to select
    Returns:
        indices: Array of indices for the top m features
    """
    # TODO
    return None

if __name__ == "__main__":
    # you are allowed to use loops here

    # TODO: Load data using pandas
    df_train = pd.read_csv('./q2_train.csv')
    df_test = pd.read_csv('./q2_test.csv')

    y_train = np.array(df_train.label)
    y_test = np.array(df_test.label)
    
    df_X_train = df_train.loc[:, ~df_train.columns.isin(("label",))]
    df_X_test = df_test.loc[:, ~df_test.columns.isin(("label",))]

    X_train = np.array(df_X_train)
    X_test = np.array(df_X_test)
    
    # TODO: Execute Task A (Vary k, use L2)
    ks = [1, 2, 5, 10, 50, 100]
    # ks = [1, 2, 5, 10, 20, 50, 100, 150, 200]
    knn = KNN(k=100)  # irrrelevant in taskA
    knn.fit(X_train, y_train)
    # print(X_test.shape)
    for k in ks:
        # break
        y_pred = knn.predict_L2(X_test, k)
        acc = compute_accuracy(y_test, y_pred)
        print(f"K={k}: {acc}")


    # TODO: Execute Task B (Standardize, then vary m for Pearson selection, use k=20, L2)
    X_train_std, X_test_std = standardize(X_train, X_test)
    knn = KNN(k=20)
    
    ms = [5, 10, 18, 50, 100, 200, 500]
    
    for m in ms:
        # break
        idxs = get_pearson_indices(X_train_std, y_train, m)
        # print(idxs)
        _X_train = X_train_std[:, idxs]
        _X_test = X_test_std[:, idxs]
        
        knn.fit(_X_train, y_train)
        y_pred = knn.predict_L2(_X_test, 20)
        acc = compute_accuracy(y_test, y_pred)
        print(f"m={m}: {acc}")

    # TODO: Execute Task C (Standardize, use all features, use k=20, L1)
    # X_train_std, X_test_std = standardize(X_train, X_test)
    knn = KNN(k=20)
    knn.fit(X_train_std, y_train)
    y_pred = knn.predict_L1(X_test_std, 20)
    acc = compute_accuracy(y_test, y_pred)
    print(f"{acc}")

    