"""Implementation of different Neural Networks with pytorch."""

import torch
import torch.nn as nn
import torch.nn.functional as functional
from .utilities import inverse_softplus

__all__ = ['DeterministicNN', 'ProbabilisticNN', 'HeteroGaussianNN', 'HomoGaussianNN',
           'CategoricalNN', 'EnsembleNN', 'FelixNet']


class DeterministicNN(nn.Module):
    """Deterministic Neural Network Implementation.

    Parameters
    ----------
    in_dim: int
        input dimension of neural network.
    out_dim: int
        output dimension of neural network.
    layers: list of int, optional
        list of width of neural network layers, each separated with a ReLU
        non-linearity.
    biased_head: bool, optional
        flag that indicates if head of NN has a bias term or not.

    """

    def __init__(self, in_dim, out_dim, layers=None, biased_head=True):
        super().__init__()
        self.layers = layers or list()

        layers_ = []

        for layer in self.layers:
            layers_.append(nn.Linear(in_dim, layer))
            layers_.append(nn.ReLU())
            in_dim = layer

        self.hidden_layers = nn.Sequential(*layers_)
        self.embedding_dim = in_dim + 1 if biased_head else in_dim
        self.head = nn.Linear(in_dim, out_dim, bias=biased_head)

    def forward(self, x):
        """Execute forward computation of the Neural Network.

        Parameters
        ----------
        x: torch.Tensor
            Tensor of size [batch_size x in_dim] where the NN is evaluated.

        Returns
        -------
        out: torch.Tensor
            Tensor of size [batch_size x out_dim].
        """
        return self.head(self.hidden_layers(x))

    def last_layer_embeddings(self, x):
        """Get last layer embeddings of the Neural Network.

        Parameters
        ----------
        x: torch.Tensor
            Tensor of size [batch_size x in_dim] where the NN is evaluated.

        Returns
        -------
        out: torch.Tensor
            Tensor of size [batch_size x embedding_dim].
        """
        out = self.hidden_layers(x)
        if self.head.bias is not None:
            out = torch.cat((out, torch.ones(out.shape[0], 1)), dim=1)
        return out


class ProbabilisticNN(DeterministicNN):
    """A Module that parametrizes a torch.distributions.Distribution distribution.

    Parameters
    ----------
    in_dim: int
        input dimension of neural network.
    out_dim: int
        output dimension of neural network.
    layers: list of int
        list of width of neural network layers, each separated with a ReLU
        non-linearity.
    biased_head: bool, optional
        flag that indicates if head of NN has a bias term or not.

    """

    def __init__(self, in_dim, out_dim, layers=None, biased_head=True):
        super().__init__(in_dim, out_dim, layers=layers, biased_head=biased_head)


class HeteroGaussianNN(ProbabilisticNN):
    """A Module that parametrizes a diagonal heteroscedastic Normal distribution."""

    def __init__(self, in_dim, out_dim, layers=None, biased_head=True,
                 squashed_output=True):
        super().__init__(in_dim, out_dim, layers=layers, biased_head=biased_head)
        in_dim = self.head.in_features
        self._covariance = nn.Linear(in_dim, out_dim, bias=biased_head)
        self.squashed_output = squashed_output

    def forward(self, x):
        """Execute forward computation of the Neural Network.

        Parameters
        ----------
        x: torch.Tensor
            Tensor of size [batch_size x in_dim] where the NN is evaluated.

        Returns
        -------
        out: torch.distributions.MultivariateNormal
            Multivariate distribution with mean of size [batch_size x out_dim] and
            covariance of size [batch_size x out_dim x out_dim].
        """
        x = self.hidden_layers(x)
        mean = self.head(x)
        if self.squashed_output:
            mean = torch.tanh(mean)

        covariance = nn.functional.softplus(self._covariance(x))
        covariance = torch.diag_embed(covariance)

        return mean, covariance


class HomoGaussianNN(ProbabilisticNN):
    """A Module that parametrizes a diagonal homoscedastic Normal distribution."""

    def __init__(self, in_dim, out_dim, layers=None, biased_head=True,
                 squashed_output=True):
        super().__init__(in_dim, out_dim, layers=layers, biased_head=biased_head)
        initial_scale = inverse_softplus(torch.ones(out_dim))
        self._covariance = nn.Parameter(initial_scale, requires_grad=True)
        self.squashed_output = squashed_output

    def forward(self, x):
        """Execute forward computation of the Neural Network.

        Parameters
        ----------
        x: torch.Tensor
            Tensor of size [batch_size x in_dim] where the NN is evaluated.

        Returns
        -------
        out: torch.distributions.MultivariateNormal
            Multivariate distribution with mean of size [batch_size x out_dim] and
            covariance of size [batch_size x out_dim x out_dim].
        """
        x = self.hidden_layers(x)
        mean = self.head(x)
        if self.squashed_output:
            mean = torch.tanh(mean)

        covariance = functional.softplus(self._covariance)
        covariance = torch.diag_embed(covariance)

        return mean, covariance


class CategoricalNN(ProbabilisticNN):
    """A Module that parametrizes a Categorical distribution."""

    def __init__(self, in_dim, out_dim, layers=None, biased_head=True):
        super().__init__(in_dim, out_dim, layers=layers, biased_head=biased_head)

    def forward(self, x):
        """Execute forward computation of the Neural Network.

        Parameters
        ----------
        x: torch.Tensor
            Tensor of size [batch_size x in_dim] where the NN is evaluated.

        Returns
        -------
        out: torch.distributions.MultivariateNormal
            Multivariate distribution with mean of size [batch_size x out_dim] and
            covariance of size [batch_size x out_dim x out_dim].
        """
        output = self.head(self.hidden_layers(x))
        return output


class EnsembleNN(ProbabilisticNN):
    """Implementation of an Ensemble of Neural Networks.

    The Ensemble shares the inner layers and then has `num_heads' different heads.
    Using these heads, it returns a Multivariate distribution parametrized by the
    mean and variance of the heads' outputs.

    Parameters
    ----------
    in_dim: int
        input dimension of neural network.
    out_dim: int
        output dimension of neural network.
    layers: list of int
        list of width of neural network layers, each separated with a ReLU
        non-linearity.
    num_heads: int
        number of heads of ensemble

    """

    def __init__(self, in_dim, out_dim, layers=None, num_heads=5):
        self.num_heads = num_heads
        super().__init__(in_dim, out_dim * num_heads, layers)

    def forward(self, x):
        """Execute forward computation of the Neural Network.

        Parameters
        ----------
        x: torch.Tensor
            Tensor of size [batch_size x in_dim] where the NN is evaluated.

        Returns
        -------
        out: torch.distributions.MultivariateNormal
            Multivariate distribution with mean of size [batch_size x out_dim] and
            covariance of size [batch_size x out_dim x out_dim].
        """
        x = self.hidden_layers(x)
        out = self.head(x)

        out = torch.reshape(out, out.shape[:-1] + (-1, self.num_heads))

        mean = torch.mean(out, dim=-1)
        covariance = torch.diag_embed(torch.var(out, dim=-1))

        return mean, covariance


class FelixNet(nn.Module):
    """A Module that implements FelixNet."""

    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.layers = [64, 64]

        self.linear1 = nn.Linear(in_dim, 64, bias=True)
        torch.nn.init.zeros_(self.linear1.bias)

        self.linear2 = nn.Linear(64, 64, bias=True)
        torch.nn.init.zeros_(self.linear2.bias)

        self._mean = nn.Linear(64, out_dim, bias=False)
        # torch.nn.init.uniform_(self._mean.weight, -0.1, 0.1)

        self._covariance = nn.Linear(64, out_dim, bias=False)
        # torch.nn.init.uniform_(self._covariance.weight, -0.01, 0.01)

    def forward(self, x):
        """Execute felix network."""
        x = torch.relu(self.linear1(x))
        x = torch.relu(self.linear2(x))

        mean = torch.tanh(self._mean(x))
        covariance = functional.softplus(self._covariance(x))
        covariance = torch.diag_embed(covariance)

        return mean, covariance
