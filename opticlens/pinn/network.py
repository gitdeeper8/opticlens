"""
Physics-Informed Neural Networks (PINNs) for atmospheric optics
Solves inverse problems and interpolates sparse measurements
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional, Union
import torch
import torch.nn as nn
import torch.optim as optim
from dataclasses import dataclass


@dataclass
class PINNConfig:
    """Configuration for PINN"""
    layers: List[int] = None  # Hidden layer sizes
    activation: str = 'tanh'
    learning_rate: float = 1e-3
    n_epochs: int = 10000
    lambda_physics: float = 1.0  # Weight for physics loss
    lambda_data: float = 1.0     # Weight for data loss
    lambda_bc: float = 1.0       # Weight for boundary conditions
    device: str = 'cpu'


class PhysicsInformedNN(nn.Module):
    """
    Physics-Informed Neural Network for atmospheric optics
    
    Solves radiative transfer equation with sparse measurements
    """
    
    def __init__(self, 
                 input_dim: int,
                 output_dim: int,
                 config: PINNConfig):
        super().__init__()
        
        self.config = config
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        # Build network architecture
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in config.layers:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            if config.activation == 'tanh':
                layers.append(nn.Tanh())
            elif config.activation == 'relu':
                layers.append(nn.ReLU())
            elif config.activation == 'sigmoid':
                layers.append(nn.Sigmoid())
            elif config.activation == 'silu':
                layers.append(nn.SiLU())
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Move to device
        self.device = torch.device(config.device)
        self.to(self.device)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return self.network(x)
    
    def radiative_transfer_residual(self, 
                                   x: torch.Tensor,
                                   I: torch.Tensor,
                                   beta_ext: torch.Tensor,
                                   beta_scat: torch.Tensor,
                                   source: torch.Tensor) -> torch.Tensor:
        """
        Compute residual of radiative transfer equation
        
        dI/ds = -β_ext·I + β_scat·∫P(Ω'→Ω)·I dΩ' + source
        """
        # Compute gradients using autograd
        I.requires_grad_(True)
        
        # Gradient with respect to spatial coordinates
        dI_dx = torch.autograd.grad(
            I, x,
            grad_outputs=torch.ones_like(I),
            create_graph=True,
            retain_graph=True
        )[0]
        
        # Streaming term (simplified 1D)
        stream_term = dI_dx[:, 0]  # dI/ds in s-direction
        
        # Extinction term
        extinction_term = -beta_ext * I
        
        # Multiple scattering term (simplified)
        # In full implementation, this would integrate over angles
        scattering_term = beta_scat * I.mean()  # Placeholder
        
        # Source term (thermal emission, etc.)
        source_term = source
        
        # Residual
        residual = stream_term - extinction_term - scattering_term - source_term
        
        return residual
    
    def physics_loss(self, 
                    collocation_points: torch.Tensor,
                    beta_ext: torch.Tensor,
                    beta_scat: torch.Tensor,
                    source: torch.Tensor) -> torch.Tensor:
        """
        Compute physics-informed loss at collocation points
        """
        I_pred = self.forward(collocation_points)
        
        residual = self.radiative_transfer_residual(
            collocation_points, I_pred, beta_ext, beta_scat, source
        )
        
        return torch.mean(residual**2)
    
    def data_loss(self,
                 data_points: torch.Tensor,
                 data_values: torch.Tensor) -> torch.Tensor:
        """
        Compute data misfit loss at measurement points
        """
        I_pred = self.forward(data_points)
        
        return torch.mean((I_pred - data_values)**2)
    
    def boundary_loss(self,
                     boundary_points: torch.Tensor,
                     boundary_values: torch.Tensor) -> torch.Tensor:
        """
        Compute boundary condition loss
        """
        I_pred = self.forward(boundary_points)
        
        return torch.mean((I_pred - boundary_values)**2)
    
    def train_step(self,
                  collocation: Dict,
                  data: Dict,
                  boundary: Dict,
                  optimizer: optim.Optimizer) -> Dict:
        """
        Single training step
        """
        optimizer.zero_grad()
        
        # Forward pass
        collocation_points = collocation['points'].to(self.device)
        data_points = data['points'].to(self.device)
        data_values = data['values'].to(self.device)
        boundary_points = boundary['points'].to(self.device)
        boundary_values = boundary['values'].to(self.device)
        
        # Physics loss
        L_phys = self.physics_loss(
            collocation_points,
            collocation.get('beta_ext', torch.ones_like(collocation_points[:, 0])),
            collocation.get('beta_scat', torch.zeros_like(collocation_points[:, 0])),
            collocation.get('source', torch.zeros_like(collocation_points[:, 0]))
        )
        
        # Data loss
        L_data = self.data_loss(data_points, data_values)
        
        # Boundary loss
        L_bc = self.boundary_loss(boundary_points, boundary_values)
        
        # Total loss
        L_total = (self.config.lambda_physics * L_phys +
                  self.config.lambda_data * L_data +
                  self.config.lambda_bc * L_bc)
        
        # Backward pass
        L_total.backward()
        optimizer.step()
        
        return {
            'total': L_total.item(),
            'physics': L_phys.item(),
            'data': L_data.item(),
            'bc': L_bc.item()
        }
    
    def fit(self,
           collocation: Dict,
           data: Dict,
           boundary: Dict,
           verbose: bool = True) -> List[Dict]:
        """
        Train the PINN
        """
        optimizer = optim.Adam(self.parameters(), lr=self.config.learning_rate)
        
        history = []
        
        for epoch in range(self.config.n_epochs):
            loss_dict = self.train_step(collocation, data, boundary, optimizer)
            history.append(loss_dict)
            
            if verbose and epoch % 1000 == 0:
                print(f"Epoch {epoch}: total={loss_dict['total']:.6f}, "
                      f"phys={loss_dict['physics']:.6f}, "
                      f"data={loss_dict['data']:.6f}, "
                      f"bc={loss_dict['bc']:.6f}")
        
        return history
    
    def predict(self, points: np.ndarray) -> np.ndarray:
        """
        Predict at new points
        """
        self.eval()
        points_tensor = torch.tensor(points, dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            I_pred = self.forward(points_tensor)
        
        return I_pred.cpu().numpy()


class AerosolRetrievalPINN(PhysicsInformedNN):
    """
    Specialized PINN for aerosol property retrieval from AERONET data
    """
    
    def __init__(self, config: PINNConfig):
        # Input: [wavelength, time, location]
        # Output: [AOD, angstrom, fine_mode_fraction, single_scattering_albedo]
        super().__init__(input_dim=3, output_dim=4, config=config)
    
    def angstrom_law_constraint(self,
                               wavelengths: torch.Tensor,
                               aod_pred: torch.Tensor) -> torch.Tensor:
        """
        Enforce Ångström wavelength dependence
        """
        # τ(λ) = β·λ^(-α)
        # Take log: log(τ) = log(β) - α·log(λ)
        
        log_lambda = torch.log(wavelengths)
        log_aod = torch.log(aod_pred)
        
        # Linear fit in log-log space
        # This should be approximately linear with slope -α
        log_lambda_mean = log_lambda.mean()
        log_aod_mean = log_aod.mean()
        
        numerator = torch.sum((log_lambda - log_lambda_mean) * (log_aod - log_aod_mean))
        denominator = torch.sum((log_lambda - log_lambda_mean)**2)
        
        alpha = -numerator / (denominator + 1e-8)
        
        # Constraint: α should be between 0 and 3
        alpha_constraint = torch.relu(alpha - 3) + torch.relu(-alpha)
        
        return alpha_constraint
    
    def physics_loss(self,
                    collocation_points: torch.Tensor,
                    beta_ext: torch.Tensor,
                    beta_scat: torch.Tensor,
                    source: torch.Tensor) -> torch.Tensor:
        """
        Override with aerosol-specific physics
        """
        # Forward pass
        outputs = self.forward(collocation_points)
        aod = outputs[:, 0]
        wavelengths = collocation_points[:, 0]
        
        # Ångström law constraint
        angstrom_loss = self.angstrom_law_constraint(wavelengths, aod)
        
        # Physical bounds constraint
        bounds_loss = torch.mean(torch.relu(-aod))  # AOD >= 0
        
        return angstrom_loss + bounds_loss


class TurbulencePINN(PhysicsInformedNN):
    """
    Specialized PINN for turbulence field reconstruction from scintillometer data
    """
    
    def __init__(self, config: PINNConfig):
        # Input: [x, y, z, t]
        # Output: [Cn2, temperature, wind_speed]
        super().__init__(input_dim=4, output_dim=3, config=config)
    
    def kolmogorov_constraint(self,
                             positions: torch.Tensor,
                             cn2_pred: torch.Tensor) -> torch.Tensor:
        """
        Enforce Kolmogorov turbulence statistics
        """
        # Structure function should follow D_n(r) = Cn2 * r^(2/3)
        
        # Sample pairs of points
        n_points = positions.shape[0]
        if n_points < 2:
            return torch.tensor(0.0)
        
        # Random pairs
        idx1 = torch.randint(0, n_points, (n_points//2,))
        idx2 = torch.randint(0, n_points, (n_points//2,))
        
        r1 = positions[idx1]
        r2 = positions[idx2]
        cn2_1 = cn2_pred[idx1]
        cn2_2 = cn2_pred[idx2]
        
        # Separation distance
        dr = torch.norm(r1 - r2, dim=1)
        
        # Structure function from predictions
        Dn_pred = torch.mean((cn2_1 - cn2_2)**2)
        
        # Theoretical structure function
        Cn2_mean = torch.mean(cn2_pred)
        Dn_theory = Cn2_mean * dr**(2/3)
        
        # Residual
        residual = torch.mean((Dn_pred - Dn_theory)**2)
        
        return residual
    
    def physics_loss(self,
                    collocation_points: torch.Tensor,
                    beta_ext: torch.Tensor,
                    beta_scat: torch.Tensor,
                    source: torch.Tensor) -> torch.Tensor:
        """
        Turbulence-specific physics loss
        """
        outputs = self.forward(collocation_points)
        cn2 = outputs[:, 0]
        
        # Kolmogorov constraint
        kolmogorov_loss = self.kolmogorov_constraint(collocation_points, cn2)
        
        # Vertical profile constraint (exponential decay with height)
        heights = collocation_points[:, 2]
        cn2_profile = 1e-15 * torch.exp(-heights / 1000)
        profile_loss = torch.mean((cn2 - cn2_profile)**2)
        
        return kolmogorov_loss + 0.1 * profile_loss
