import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data

class RoadGNN(nn.Module):
    def __init__(self, num_node_features, hidden_channels, out_channels):
        super(RoadGNN, self).__init__()
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index, edge_weight=None):
        x = self.conv1(x, edge_index, edge_weight)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index, edge_weight)
        return x

class GNNEmbedder:
    def __init__(self, num_features=5, hidden=16, out=8):
        self.model = RoadGNN(num_features, hidden, out)
    
    def get_embeddings(self, node_features, edge_index, edge_weights=None):
        """
        node_features: Tensor (N, F)
        edge_index: Tensor (2, E)
        """
        self.model.eval()
        with torch.no_grad():
            embeddings = self.model(node_features, edge_index, edge_weights)
        return embeddings

if __name__ == "__main__":
    # Dummy graph
    x = torch.randn(12, 5) # 12 districts, 5 features
    edge_index = torch.randint(0, 12, (2, 20))
    embedder = GNNEmbedder()
    emb = embedder.get_embeddings(x, edge_index)
    print("Embeddings shape:", emb.shape)
