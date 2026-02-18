### Translate Coordinate System

Translate Left hand coordinate system used in Unity3D, to Right Hand coordinate system, following the covecntion of OpenCV (standard Computer Vison camera look orientation).

photo -> photo

Get the transform matrix from Unity3D, and flip the values of Y and Z for translation vector only.

The tranform vector (camera intrinsic matrix) looks like the following:

This homogeneous transformation is composed out of R, a 3-by-3 rotation matrix, and t, a 3-by-1 translation vector:

$$
\begin{bmatrix}
R & t  \\
0 & 1  \\
\end{bmatrix}
$$

$$
\eq
\begin{bmatrix}
r_{11} & r_{11} & r_{11} & t_{x} \\
r_{21} & r_{22} & r_{23} & t_{y} \\
r_{31} & r_{32} & r_{33} & t_{z} \\
0 & 0 & 0 & 1 \\
\end{bmatrix}
$$

The top 3x3 matrix is the Rotation Matrix, whereas, the top-3 values of the last column is the translation matrix (repsenting the camera position)
