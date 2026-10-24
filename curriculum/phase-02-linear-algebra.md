# Phase 02: Linear Algebra

*Lineare Algebra*

Systems of equations, matrices and eigenvalues, the machinery behind every solver in this course.

- **ETH reference:** Lineare Algebra 1 / Lineare Algebra 2
- **Real-world anchors:** Every truss, every FEM mesh, every Swiss bridge is a matrix
- **Lessons:** 16

## 02.01 Vectors and geometry

**Goal:** Represent forces and positions as vectors

- **Derive by hand:** Dot product, cross product, projections
- **Code from scratch:** Vector toolkit: projection, angle, area via cross product
- **Interactive lab:** 3D vector playground with draggable arrows
- **Test that proves it:** Cross product is orthogonal to both inputs within 1e-12
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.02 Systems of linear equations

**Goal:** Turn equilibrium into Ax = b

- **Derive by hand:** Row picture vs column picture
- **Code from scratch:** Write a truss joint equilibrium system by hand for 3 joints
- **Interactive lab:** Two-line intersection and column combination views
- **Test that proves it:** Your system reproduces hand-solved forces
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.03 Gaussian elimination

**Goal:** Solve Ax = b from scratch

- **Derive by hand:** Elimination as a sequence of elementary matrices
- **Code from scratch:** Implement Gaussian elimination with partial pivoting
- **Interactive lab:** Step-through elimination animation
- **Test that proves it:** Matches numpy.linalg.solve to 1e-10 on random 50x50 systems
- **Pro tool:** LAPACK via NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.04 LU decomposition

**Goal:** Factor once, solve many load cases

- **Derive by hand:** A = PLU
- **Code from scratch:** Implement LU and forward/back substitution
- **Interactive lab:** Multiple load cases on one bridge reuse the factorisation
- **Test that proves it:** Reconstruct PA = LU within 1e-12
- **Pro tool:** scipy.linalg.lu
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.05 Determinants and invertibility

**Goal:** Know when a structure is a mechanism

- **Derive by hand:** det as signed volume; det = 0 means singular
- **Code from scratch:** Detect a missing truss member via near-zero determinant
- **Interactive lab:** Delete a member, watch det go to zero ([Break the bridge](#lab-truss))
- **Test that proves it:** Mechanism truss yields condition number above 1e12
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.06 Vector spaces and rank

**Goal:** Count independent equations and unknowns

- **Derive by hand:** Rank-nullity theorem
- **Code from scratch:** Compute rank via elimination; find null space
- **Interactive lab:** Null-space visualiser: rigid-body modes of an unsupported truss
- **Test that proves it:** Free 2D truss has a 3-dimensional null space
- **Pro tool:** SciPy null_space
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.07 Orthogonality and least squares

**Goal:** Fit models to noisy measurements

- **Derive by hand:** Normal equations A^T A x = A^T b, projection
- **Code from scratch:** Fit a calibration line to strain-gauge data
- **Interactive lab:** Residuals shown as vertical bars
- **Test that proves it:** Matches numpy.linalg.lstsq
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.08 QR and Gram-Schmidt

**Goal:** Solve least squares stably

- **Derive by hand:** Gram-Schmidt orthogonalisation, A = QR
- **Code from scratch:** Implement modified Gram-Schmidt and solve least squares
- **Interactive lab:** Orthogonalisation animation in 3D
- **Test that proves it:** Q^T Q = I within 1e-12
- **Pro tool:** numpy.linalg.qr
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.09 Eigenvalues and eigenvectors

**Goal:** Find the natural directions of a linear map

- **Derive by hand:** det(A - lambda I) = 0
- **Code from scratch:** Power iteration and inverse iteration
- **Interactive lab:** Unit circle mapped to an ellipse with eigenvectors highlighted
- **Test that proves it:** Power iteration finds the dominant eigenvalue within 1e-8
- **Pro tool:** numpy.linalg.eig
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.10 Symmetric matrices and the spectral theorem

**Goal:** Understand why stiffness matrices behave nicely

- **Derive by hand:** Real eigenvalues, orthogonal eigenvectors
- **Code from scratch:** Jacobi eigenvalue algorithm for symmetric matrices
- **Interactive lab:** Rotation sweeps zeroing off-diagonals
- **Test that proves it:** Eigenvalues match numpy.linalg.eigh
- **Pro tool:** SciPy eigh
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.11 Positive definiteness and energy

**Goal:** Connect matrices to strain energy

- **Derive by hand:** x^T K x > 0 for a stable structure
- **Code from scratch:** Cholesky factorisation from scratch
- **Interactive lab:** Energy bowl surface for a 2-DOF spring system
- **Test that proves it:** Cholesky fails exactly when matrix is indefinite
- **Pro tool:** scipy.linalg.cholesky
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.12 Singular value decomposition

**Goal:** Find the most important modes of any data

- **Derive by hand:** A = U Sigma V^T
- **Code from scratch:** SVD via eigen-decomposition of A^T A; low-rank image of a Swiss landscape
- **Interactive lab:** Rank slider reconstructing an image
- **Test that proves it:** Rank-k error equals the (k+1)th singular value in 2-norm
- **Pro tool:** numpy.linalg.svd
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.13 Coordinate transformations

**Goal:** Rotate frames without mistakes

- **Derive by hand:** Rotation matrices, orthogonality, composition
- **Code from scratch:** Rotate a stress tensor and a force between frames
- **Interactive lab:** Rotating frame gizmo
- **Test that proves it:** R^T R = I and det R = 1
- **Pro tool:** scipy.spatial.transform
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.14 Sparse matrices

**Goal:** Solve systems with millions of unknowns

- **Derive by hand:** Sparsity patterns, fill-in
- **Code from scratch:** CSR storage and sparse matrix-vector product
- **Interactive lab:** Sparsity spy plot of a 2D mesh Laplacian
- **Test that proves it:** CSR matvec equals dense matvec
- **Pro tool:** scipy.sparse
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.15 Iterative solvers

**Goal:** Solve huge systems without factorising

- **Derive by hand:** Jacobi, Gauss-Seidel convergence via spectral radius
- **Code from scratch:** Implement conjugate gradient
- **Interactive lab:** Residual history plot
- **Test that proves it:** CG converges in at most n steps in exact arithmetic on SPD systems (check small n)
- **Pro tool:** scipy.sparse.linalg.cg
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.16 Linear maps in mechanics

**Goal:** See statics, FEM and vibration as the same algebra

- **Derive by hand:** K u = f, M u'' + K u = 0
- **Code from scratch:** Unify a spring chain as K u = f and as an eigenproblem
- **Interactive lab:** Spring chain with static and modal views
- **Test that proves it:** Static solution satisfies equilibrium at every node
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2
