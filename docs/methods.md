# Numerical methods

`ApophisSimulation` uses REBOUND's adaptive IAS15 integrator in AU, Julian years, and solar masses. Initial conditions are obtained through REBOUND's Horizons interface. The default model contains the Sun, eight planets, and the Moon; users may provide another body sequence when their scientific question requires it.

The analytical module solves elliptic Kepler's equation by Newton iteration and rotates perifocal coordinates with the conventional 3-1-3 Euler sequence. The patched-conics function derives Earth-relative hyperbolic elements from a state vector within the Earth sphere of influence. Analytical estimates are intended for comparison and pedagogy, not as a substitute for the N-body solution.

All numerical minima are sampled minima. Increase `steps`, or use a local refinement workflow, when reporting a close-approach epoch or distance at high precision.
