import numpy as np
import torch
import torch.nn as nn
from dataclasses import dataclass, asdict
from engine.chess import rules
from engine.encoding.position_encoder import encode, NUM_PLANES
from engine.encoding.move_encoder import move_to_index, ACTION_SPACE_SIZE, PLANES_PER_SQUARE

assert 64 * PLANES_PER_SQUARE == ACTION_SPACE_SIZE

@dataclass
class ModelConfig:
  num_planes: int = NUM_PLANES
  channels: int = 128
  blocks: int = 10
  value_channels: int = 32
  value_hidden: int = 256

def _conv_bn_relu(in_channels, out_channels, kernel):
  return nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel, padding=kernel // 2, bias=False), nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True))

class ResidualBlock(nn.Module):
  def __init__(self, channels):
    super().__init__()
    self.conv1, self.bn1 = nn.Conv2d(channels, channels, 3, padding=1, bias=False), nn.BatchNorm2d(channels)
    self.conv2, self.bn2 = nn.Conv2d(channels, channels, 3, padding=1, bias=False), nn.BatchNorm2d(channels)

  def forward(self, x):
    out = torch.relu(self.bn1(self.conv1(x)))
    out = self.bn2(self.conv2(out))
    return torch.relu(out + x)

class PolicyHead(nn.Module):
  def __init__(self, channels):
    super().__init__()
    self.body = _conv_bn_relu(channels, channels, 3)
    self.out = nn.Conv2d(channels, PLANES_PER_SQUARE, 1)

  def forward(self, x):
    return self.out(self.body(x)).permute(0, 2, 3, 1).reshape(x.shape[0], -1)

class ValueHead(nn.Module):
  def __init__(self, channels, value_channels, hidden):
    super().__init__()
    self.body = _conv_bn_relu(channels, value_channels, 1)
    self.fc = nn.Sequential(nn.Flatten(), nn.Linear(value_channels * 64, hidden), nn.ReLU(inplace=True), nn.Linear(hidden, 1), nn.Tanh())

  def forward(self, x):
    return self.fc(self.body(x)).squeeze(1)

class ChessNet(nn.Module):
  def __init__(self, config=None):
    super().__init__()
    self.config = config or ModelConfig()
    c = self.config
    self.stem = _conv_bn_relu(c.num_planes, c.channels, 3)
    self.tower = nn.Sequential(*[ResidualBlock(c.channels) for _ in range(c.blocks)])
    self.policy_head = PolicyHead(c.channels)
    self.value_head = ValueHead(c.channels, c.value_channels, c.value_hidden)

  def features(self, x):
    return self.tower(self.stem(x))

  def forward(self, x):
    features = self.features(x)
    return self.policy_head(features), self.value_head(features)

def count_parameters(model):
  return sum(p.numel() for p in model.parameters() if p.requires_grad)

def save_checkpoint(model, path, extra=None):
  torch.save({'config': asdict(model.config), 'action_space_size': ACTION_SPACE_SIZE, 'state_dict': model.state_dict(), 'extra': extra or {}}, path)

def load_checkpoint(path, map_location='cpu'):
  data = torch.load(path, map_location=map_location)
  if data['action_space_size'] != ACTION_SPACE_SIZE or data['config']['num_planes'] != NUM_PLANES:
    raise ValueError(f'checkpoint was built with planes={data["config"]["num_planes"]}, actions={data["action_space_size"]}; current encoding is planes={NUM_PLANES}, actions={ACTION_SPACE_SIZE}')
  model = ChessNet(ModelConfig(**data['config']))
  model.load_state_dict(data['state_dict'])
  return model, data['extra']

@torch.no_grad()
def predict(model, state):
  was_training = model.training
  model.eval()
  device = next(model.parameters()).device
  moves = rules.legal_moves(state)
  logits, value = model(torch.from_numpy(encode(state)).unsqueeze(0).to(device))
  indices = torch.tensor([move_to_index(m, state) for m in moves], dtype=torch.long, device=device)
  probs = torch.softmax(logits[0, indices], dim=0).cpu().numpy()
  model.train(was_training)
  return moves, probs, float(value[0])