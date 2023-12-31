"""Show fenics mesh and displacement solution."""
from dolfin import *

# Create mesh and define function space
mesh = UnitCubeMesh(12, 12, 12)
V = VectorFunctionSpace(mesh, "Lagrange", 1)

# Mark boundary subdomains
left  = CompiledSubDomain("near(x[0], side) && on_boundary", side=0.0)
right = CompiledSubDomain("near(x[0], side) && on_boundary", side=1.0)

# Define Dirichlet boundary (x=0 or x=1)
c = Constant((0.0, 0.0, 0.0))
r = Expression((
        "scale*0.0",
        "scale*(y0 + (x[1]-y0)*cos(theta) - (x[2]-z0)*sin(theta)-x[1])",
        "scale*(z0 + (x[1]-y0)*sin(theta) + (x[2]-z0)*cos(theta)-x[2])",
    ), scale=0.5, y0=0.5, z0=0.5, theta=pi/4, degree=2)
bcl = DirichletBC(V, c, left)
bcr = DirichletBC(V, r, right)

w = TrialFunction(V)  # Incremental displacement
v = TestFunction(V)   # Test function
u = Function(V)       # Solution

solve(inner(grad(w), grad(v)) * dx == inner(c, v) * dx, u, [bcl, bcr])


########################################################### vedo
from vedo.dolfin import plot

plot(u, mode='displacements', azimuth=45)
