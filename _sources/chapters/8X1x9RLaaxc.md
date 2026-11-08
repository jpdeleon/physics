# Mod-01 Lec-02 Newtonian mechanics

````{tabs}
```{tab} Abstract
This lecture introduces the formal study of classical dynamics, specifically Newtonian mechanics, by focusing on the concept of degrees of freedom. The instructor explains how to count these independent coordinates for systems of particles, distinguishing between unconstrained systems, holonomic constraints (which reduce degrees of freedom), and non-holonomic constraints (inequalities or velocity-dependent restrictions). The lecture establishes that a rigid body always possesses exactly six degrees of freedom: three for the translational motion of its center of mass and three for its rotational orientation. It further distinguishes between holonomic and non-holonomic constraints, noting that the latter do not necessarily reduce the count of independent coordinates. Finally, the video transitions to the concept of phase space, defining it as the space of positions and velocities required to uniquely determine a system's future evolution. The analysis of a simple harmonic oscillator demonstrates how the geometry of phase trajectories reveals system properties like energy conservation and the amplitude-independence of the oscillation period.
```
```{tab} Key Insights

- The number of independent degrees of freedom is determined by taking the total coordinates (3N for N particles) and subtracting independent holonomic constraints.

- A rigid body, regardless of the number of constituent particles, always has exactly 6 degrees of freedom: 3 translational and 3 rotational.

- Holonomic constraints are equality relations involving only coordinates that allow the reduction of degrees of freedom, whereas non-holonomic constraints involve inequalities or velocities and do not reduce degrees of freedom.

- Newtonian equations of motion are second-order differential equations, requiring initial positions and velocities to predict future motion uniquely.

- The complete set of dynamical variables is generalized coordinates q and their time derivatives, the generalized velocities q_dot, forming the phase space.

- In an autonomous system, phase trajectories cannot intersect themselves or each other because the future must be uniquely determined by the initial condition.

- For a one-dimensional conservative system, the phase trajectory is a curve defined by the conservation of total energy, E = T + V.

- The phase trajectory of a simple harmonic oscillator is an ellipse in phase space, where the area relates to the system's energy.

```
```{tab} Deep Dive
### Core Concepts

The central idea is that to describe the state of a physical system and predict its future evolution, one must first identify its independent degrees of freedom. For a system of N free particles, there are 3N coordinates. However, if constraints are applied, such as fixing the distance between particles (forming a rigid body), we must determine which constraints are independent. For a rigid body, despite having many internal constraints, only 6 are independent: 3 describing the position of the center of mass and 3 describing the orientation (e.g., via Euler angles). The lecture introduces phase space, a mathematical construct where coordinates and velocities are independent variables. The state of a system at any instant is a point in this space, and the equation of motion traces a trajectory. A key principle is that in autonomous systems, these trajectories cannot intersect; if they did, a single initial point would lead to two different futures, violating determinism. The analysis shifts from solving differential equations explicitly to studying the geometry of these trajectories in phase space, which often reveals conserved quantities like energy.


### Equations


$$3N - Nc = n$$


$$F = m * q_ddot$$


$$q_dot = v, v_dot = -kq/m$$


$$1/2 * m * v^2 + V(q) = E$$


$$dv/dq = -omega^2 * q / v$$



### Examples & Applications

The lecture uses a particle falling under gravity to explain why initial velocity is needed in addition to position to predict the path (parabolic or elliptic orbits). It contrasts a free particle with a particle on a plane (constrained to 2 degrees of freedom) and a rigid triangle of three particles (constrained to 6 degrees of freedom). The simple harmonic oscillator is analyzed in detail, showing that its phase trajectory is an ellipse centered at the origin. The instructor explains that different energies correspond to concentric ellipses, and the case of zero energy corresponds to the equilibrium point at the origin, which is a trajectory itself.
```
```{tab} Video
[![Watch on YouTube](https://img.youtube.com/vi/8X1x9RLaaxc/maxresdefault.jpg)](https://www.youtube.com/watch?v=8X1x9RLaaxc)

[Watch on YouTube ↗](https://www.youtube.com/watch?v=8X1x9RLaaxc)
```
````
