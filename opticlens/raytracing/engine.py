"""
Ray tracing engine for atmospheric optics
Propagates rays through 3D refractive index fields
"""

import numpy as np
from typing import Callable, Tuple, List, Optional, Dict
from dataclasses import dataclass
from scipy.integrate import solve_ivp
from opticlens.utils.constants import *


@dataclass
class Ray:
    """Ray properties"""
    position: np.ndarray  # [x, y, z] [m]
    direction: np.ndarray  # unit vector
    wavelength: float  # [μm]
    intensity: float = 1.0
    path_length: float = 0.0
    optical_path: float = 0.0


@dataclass
class RayBundle:
    """Bundle of rays for Monte Carlo simulation"""
    rays: List[Ray]
    n_rays: int
    divergence: float  # beam divergence [rad]


class RayTracingEngine:
    """
    Volumetric ray tracing through refractive index field
    
    Solves the ray equation:
    d(n·dr/ds)/ds = ∇n(r)
    """
    
    def __init__(self, refractive_index_field: Callable[[np.ndarray], float]):
        """
        Parameters
        ----------
        refractive_index_field : callable
            Function n(x,y,z) returning refractive index at point
        """
        self.n_field = refractive_index_field
        self.rays = []
        
    def ray_equation(self, s: float, y: np.ndarray) -> np.ndarray:
        """
        Ray equation in Hamiltonian form
        
        y = [x, y, z, kx, ky, kz] where k = n·dr/ds
        
        dy/ds = [k/n, ∇n]
        """
        r = y[0:3]
        k = y[3:6]
        
        n = self.n_field(r)
        
        # Compute gradient of refractive index (finite differences)
        eps = 1.0  # m
        grad_n = np.zeros(3)
        
        for i in range(3):
            r_plus = r.copy()
            r_minus = r.copy()
            r_plus[i] += eps
            r_minus[i] -= eps
            
            n_plus = self.n_field(r_plus)
            n_minus = self.n_field(r_minus)
            
            grad_n[i] = (n_plus - n_minus) / (2 * eps)
        
        return np.array([
            k[0] / n,
            k[1] / n,
            k[2] / n,
            grad_n[0],
            grad_n[1],
            grad_n[2]
        ])
    
    def trace_ray(self,
                 start_point: np.ndarray,
                 initial_direction: np.ndarray,
                 wavelength: float,
                 max_length: float = 10000,
                 n_steps: int = 1000) -> Ray:
        """
        Trace a single ray through the atmosphere
        
        Parameters
        ----------
        start_point : ndarray
            Initial position [x, y, z] [m]
        initial_direction : ndarray
            Initial direction unit vector
        wavelength : float
            Wavelength [μm]
        max_length : float
            Maximum path length [m]
        n_steps : int
            Number of integration steps
            
        Returns
        -------
        Ray
            Traced ray with path
        """
        # Normalize direction
        initial_direction = initial_direction / np.linalg.norm(initial_direction)
        
        # Initial optical wave vector k = n·dr/ds
        n0 = self.n_field(start_point)
        k0 = n0 * initial_direction
        
        # Initial state
        y0 = np.array([start_point[0], start_point[1], start_point[2],
                       k0[0], k0[1], k0[2]])
        
        # Solve ray equation
        s_span = (0, max_length)
        s_eval = np.linspace(0, max_length, n_steps)
        
        solution = solve_ivp(
            self.ray_equation,
            s_span,
            y0,
            method='RK45',
            t_eval=s_eval,
            rtol=1e-6,
            atol=1e-9
        )
        
        # Extract ray path
        positions = solution.y[0:3].T
        ks = solution.y[3:6].T
        
        # Compute optical path length
        optical_path = 0
        for i in range(1, len(positions)):
            ds = np.linalg.norm(positions[i] - positions[i-1])
            n_avg = (self.n_field(positions[i]) + self.n_field(positions[i-1])) / 2
            optical_path += n_avg * ds
        
        # Create ray object
        ray = Ray(
            position=positions[-1],
            direction=ks[-1] / np.linalg.norm(ks[-1]),
            wavelength=wavelength,
            path_length=max_length,
            optical_path=optical_path
        )
        
        # Store full path (optional)
        ray.path = positions
        ray.k_vectors = ks
        
        return ray
    
    def trace_bundle(self,
                    start_point: np.ndarray,
                    mean_direction: np.ndarray,
                    divergence: float,
                    n_rays: int,
                    wavelength: float,
                    max_length: float = 10000) -> RayBundle:
        """
        Trace a bundle of rays with angular divergence
        
        Parameters
        ----------
        start_point : ndarray
            Initial position
        mean_direction : ndarray
            Mean direction unit vector
        divergence : float
            Beam divergence [rad]
        n_rays : int
            Number of rays in bundle
        wavelength : float
            Wavelength [μm]
        max_length : float
            Maximum path length
            
        Returns
        -------
        RayBundle
            Bundle of traced rays
        """
        # Generate random directions within divergence cone
        rays = []
        
        # Create orthonormal basis
        z_axis = mean_direction / np.linalg.norm(mean_direction)
        
        # Find perpendicular vectors
        if abs(z_axis[0]) < 0.9:
            x_axis = np.cross(z_axis, [1, 0, 0])
        else:
            x_axis = np.cross(z_axis, [0, 1, 0])
        x_axis = x_axis / np.linalg.norm(x_axis)
        y_axis = np.cross(z_axis, x_axis)
        
        for i in range(n_rays):
            # Random direction within cone
            theta = np.random.uniform(0, divergence)
            phi = np.random.uniform(0, 2*np.pi)
            
            dx = np.sin(theta) * np.cos(phi)
            dy = np.sin(theta) * np.sin(phi)
            dz = np.cos(theta)
            
            direction = dx * x_axis + dy * y_axis + dz * z_axis
            direction = direction / np.linalg.norm(direction)
            
            ray = self.trace_ray(start_point, direction, wavelength, max_length)
            rays.append(ray)
        
        return RayBundle(rays=rays, n_rays=n_rays, divergence=divergence)
    
    def trace_grid(self,
                  start_points: np.ndarray,
                  directions: np.ndarray,
                  wavelengths: np.ndarray,
                  max_length: float = 10000) -> List[Ray]:
        """
        Trace multiple rays from grid of start points/directions
        
        Parameters
        ----------
        start_points : ndarray
            Array of start points (N x 3)
        directions : ndarray
            Array of directions (N x 3)
        wavelengths : ndarray
            Array of wavelengths (N)
        max_length : float
            Maximum path length
            
        Returns
        -------
        list
            List of traced rays
        """
        rays = []
        
        for i in range(len(start_points)):
            ray = self.trace_ray(
                start_points[i],
                directions[i],
                wavelengths[i],
                max_length
            )
            rays.append(ray)
        
        return rays
    
    def mirage_simulation(self,
                         observer_height: float,
                         target_distance: float,
                         temperature_gradient: float,
                         pressure: float = STANDARD_PRESSURE,
                         wavelength: float = 0.55) -> Dict:
        """
        Simulate inferior mirage over hot surface
        
        Parameters
        ----------
        observer_height : float
            Observer eye height [m]
        target_distance : float
            Distance to target [m]
        temperature_gradient : float
            Vertical temperature gradient near surface [K/m]
        pressure : float
            Atmospheric pressure [Pa]
        wavelength : float
            Wavelength [μm]
            
        Returns
        -------
        dict
            Mirage simulation results
        """
        from opticlens.refraction.edlen import EdlenRefractiveIndex
        
        edlen = EdlenRefractiveIndex()
        
        # Create refractive index profile with strong gradient near surface
        def n_profile(r):
            z = r[2]  # height
            if z < 0:
                z = 0
            
            # Temperature profile
            T_surface = 320  # K (hot surface)
            T_air = 300  # K
            T = T_surface + temperature_gradient * z
            if T < T_air:
                T = T_air + 0.1 * z
            
            return edlen.compute(pressure, T, wavelength)
        
        # Update refractive index field
        self.n_field = n_profile
        
        # Trace rays at different initial angles
        rays = []
        angles = np.linspace(-0.1, 0.01, 20)  # rad (negative = downward)
        
        for angle in angles:
            direction = np.array([0, np.sin(angle), np.cos(angle)])
            start = np.array([0, 0, observer_height])
            
            ray = self.trace_ray(start, direction, wavelength, target_distance)
            rays.append(ray)
        
        # Find which rays reach target
        target_pos = np.array([target_distance, 0, 0])
        
        rays_at_target = []
        for ray in rays:
            if np.linalg.norm(ray.position - target_pos) < 10:
                rays_at_target.append(ray)
        
        # Compute apparent displacement
        if rays_at_target:
            apparent_angle = rays_at_target[0].direction[1] / rays_at_target[0].direction[2]
            geometric_angle = observer_height / target_distance
            displacement = (apparent_angle - geometric_angle) * target_distance
        else:
            displacement = None
        
        return {
            'rays': rays,
            'rays_at_target': rays_at_target,
            'displacement': displacement,
            'observer_height': observer_height,
            'target_distance': target_distance
        }
    
    def plot_rays(self, rays: List[Ray], ax=None):
        """
        Plot ray paths (requires matplotlib)
        """
        try:
            import matplotlib.pyplot as plt
            
            if ax is None:
                fig, ax = plt.subplots(figsize=(10, 6))
            
            for ray in rays:
                if hasattr(ray, 'path'):
                    path = ray.path
                    ax.plot(path[:, 0], path[:, 2], 'b-', alpha=0.5)
            
            ax.set_xlabel('Distance [m]')
            ax.set_ylabel('Height [m]')
            ax.grid(True, alpha=0.3)
            
            return ax
            
        except ImportError:
            print("Matplotlib not available for plotting")
            return None
