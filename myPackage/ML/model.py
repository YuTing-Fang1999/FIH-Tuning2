# Pytorch
import torch.nn as nn
class My_Model(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(My_Model, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 16, bias=False),
            # nn.ReLU(),
            nn.PReLU(),

            nn.Linear(16, 8, bias=False),
            # nn.ReLU(),
            nn.PReLU(),

            nn.Linear(8, 4, bias=False),
            # nn.ReLU(),
            nn.PReLU(),

            nn.Linear(4, output_dim),
        )

    def forward(self, x):
        x = self.layers(x)
        return x