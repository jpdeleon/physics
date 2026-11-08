# Differential equations, a tourist's guide | DE1

````{tabs}
```{tab} Abstract
This video offers a tour of differential equations, describing them as the language of physics and change. It contrasts the simplicity of solving basic equations like projectile motion with the complexity of real-world systems like pendulums, where forces depend on position and velocity. The presenter argues that while exact analytic solutions are often impossible or useless due to chaos, we can still gain deep understanding by analyzing the equations' structure directly. A key method introduced is visualizing systems in a 'phase space' (state space) as vector fields, which reveals hidden dynamics, stability, and connections between seemingly unrelated systems, such as a pendulum and romantic relationships.
```
```{tab} Key Insights

- Differential equations describe systems by defining rates of change rather than static values, allowing us to model dynamics in physics, biology, and social sciences.

- Simple examples like projectile motion involve constant acceleration, but realistic systems like pendulums involve acceleration that depends on position (sine of angle) and velocity (damping).

- Real pendulums do not follow perfect sine waves because the governing equation contains a nonlinearity (the sine function) that breaks the simple harmonic motion approximation.

- Many differential equations do not have closed-form analytic solutions, especially when damping is included, so mathematicians often skip solving for the function and instead study the equation's properties directly.

- State space or phase space is a powerful tool that plots a system's variables (e.g., angle and angular velocity) against each other, turning the problem into a visualization of trajectories.

- Vector fields represent the rate of change at every point in phase space, guiding the system's evolution and revealing fixed points and stability patterns.

- Complex systems like the three-body problem exist in high-dimensional phase spaces where tiny changes in initial conditions lead to vastly different outcomes, a concept central to chaos theory.

- Even when equations come from very different contexts, such as planetary mechanics and human affection, their underlying mathematical structure in phase space can reveal deep similarities.

```
```{tab} Deep Dive
### Core Concepts

The central idea is that differential equations allow us to predict the future state of a system based on its current state and how it is changing. We start with simple cases where acceleration is constant, leading to a quadratic position function. We then move to cases where forces depend on position, creating a feedback loop where the system's state dictates its own rate of change. The video introduces the concept of reducing high-order equations into systems of first-order equations by treating the system as a point moving through a higher-dimensional space. This leads to the concept of phase space, where we can visualize the entire history of possible states as trajectories. A crucial insight is that understanding often comes not from solving for the specific function y(t), but from analyzing the vector field that dictates how the system flows through its state space. This approach allows us to determine stability (whether a system returns to equilibrium after a nudge) and visualize complex behaviors like spiraling damping or chaotic paths.


### Equations


$$y-double-dot = -g$$

$$x = L * theta$$

$$x-double-dot = -g * sin(theta)$$

$$theta-double-dot = -(g/L) * sin(theta) - mu * theta-dot$$

$$theta_new = theta + theta-dot * delta-t$$

$$theta-dot-new = theta-dot + theta-double-dot * delta-t$$



### Examples & Applications

The video uses the trajectory of a thrown object with constant gravity as the simplest example. It then applies this to planetary motion where gravity depends on distance. A pendulum is the primary case study, first approximated for small angles, then treated realistically with large angles and air resistance. The pendulum's phase space is visualized as a 2D plane of angle vs. angular velocity, showing trajectories that spiral inward. The romantic relationship model (love dynamics) is used to demonstrate how equations from physics can structurally resemble social interactions. Finally, a Python loop example demonstrates the basic numerical method for approximating solutions when exact formulas are unavailable.
```
```{tab} Video
[![Watch on YouTube](https://img.youtube.com/vi/p_di4Zn4wz4/maxresdefault.jpg)](https://www.youtube.com/watch?v=p_di4Zn4wz4)

[Watch on YouTube ↗](https://www.youtube.com/watch?v=p_di4Zn4wz4)
```
````
