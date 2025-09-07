import numpy as np

class LinUCB:
    """A simple LinUCB implementation for discrete actions with context vectors.

    Each action a has parameters theta_a estimated via ridge regression on (x, r).
    The UCB score is: p = theta_a^T x + alpha * sqrt( x^T A_a^{-1} x )
    where A_a is the Gram matrix for action a.
    """
    def __init__(self, n_actions: int, dim: int, alpha: float = 0.25):
        self.n_actions = n_actions
        self.dim = dim
        self.alpha = alpha
        # For each action a: A_a (dim x dim), b_a (dim)
        self.A = [np.eye(dim) for _ in range(n_actions)]
        self.b = [np.zeros((dim, 1)) for _ in range(n_actions)]

    def select(self, x: np.ndarray) -> int:
        """Select action for context x (dim,)."""
        x = x.reshape(-1, 1)
        scores = []
        for a in range(self.n_actions):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a]
            exploit = float((theta.T @ x)[0][0])
            explore = self.alpha * float(np.sqrt(x.T @ A_inv @ x))
            scores.append(exploit + explore)
        return int(np.argmax(scores))

    def update(self, x: np.ndarray, a: int, r: float):
        """Update parameters with observed reward r for action a given context x."""
        x = x.reshape(-1, 1)
        self.A[a] += x @ x.T
        self.b[a] += r * x