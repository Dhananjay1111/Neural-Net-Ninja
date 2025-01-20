import unittest
from parameterized import parameterized
import numpy as np
import torch

from pcnn.losses import TverskyLoss


class TestTverskyLoss(unittest.TestCase):
    @parameterized.expand([
        ("mean", 0.5, 0.5, 1.0, np.array(0.0)),
        ("sum", 0.5, 0.5, 1.0, np.array(0.0)),
    ])
    def test_all_true(self, reduction: str, alpha: float, beta: float, epsilon: float, expected_loss: np.ndarray):
        """
        Tests that the Tversky loss is computed correctly when all predictions are correct.
        """
        prediction = torch.as_tensor(
            [
                [0, 0, 1],
                [1, 0, 0],
                [0, 1, 0]
            ],
            dtype=torch.float
        )

        target = torch.as_tensor([2, 0, 1])

        loss_module = TverskyLoss(apply_softmax=False, alpha=alpha, beta=beta, epsilon=epsilon, reduction=reduction)

        actual_loss = loss_module(prediction, target).numpy()

        np.testing.assert_equal(expected_loss, actual_loss)

    @parameterized.expand([
        ("mean", np.array([0.1, 0.2, 0.7]), np.array([
            0.1 * (1 - (0.8 + 1) / (0.8 + 0.3 * 0.5 + 0.7 * 0.6 + 1)),
            0.2 * (1 - (0.25 + 1) / (0.25 + 0.3 * 1 + 0.7 * 0.1 + 1)),
            0.7 * (1 - (0.1 + 1) / (0.1 + 0.3 * 0.25 + 0.7 * 1 + 1))
        ]).mean())
    ])
    def test_weighted_loss(self, reduction: str, weight: np.ndarray, expected_loss: np.ndarray):
        """Tests that the Tversky loss is computed correctly when class weights are provided."""
        prediction = torch.as_tensor(
            [
                [0.5, 0.25, 0.25],
                [0.8, 0.1, 0.1],
                [0.6, 0.3, 0.1]
            ],
            dtype=torch.float
        )

        target = torch.as_tensor([1, 0, 2])

        loss_module = TverskyLoss(apply_softmax=False, alpha=0.3, beta=0.7, epsilon=1, reduction=reduction,
                                  weight=torch.from_numpy(weight).float())

        actual_loss = loss_module(prediction, target).numpy()

        np.testing.assert_allclose(expected_loss, actual_loss, atol=1e-07)


if __name__ == '__main__':
    unittest.main(exit=False)