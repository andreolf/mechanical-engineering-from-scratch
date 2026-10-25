// plate with a hole, quarter model (Gmsh .geo)
a = 1.0; w = 10.0; h = 0.08;
Point(1) = {a, 0, 0, h}; Point(2) = {w, 0, 0, 1.0}; Point(3) = {w, w, 0, 1.0};
Point(4) = {0, w, 0, 1.0}; Point(5) = {0, a, 0, h}; Point(6) = {0, 0, 0, h};
Line(1) = {1, 2}; Line(2) = {2, 3}; Line(3) = {3, 4}; Line(4) = {4, 5};
Circle(5) = {5, 6, 1};
Curve Loop(1) = {1, 2, 3, 4, 5}; Plane Surface(1) = {1};
Physical Curve("symmetry_y", 1) = {1}; Physical Curve("load", 2) = {2};
Physical Curve("symmetry_x", 4) = {4}; Physical Surface("plate", 10) = {1};
