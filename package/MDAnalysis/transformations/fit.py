# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- https://www.mdanalysis.org
# Copyright (c) 2006-2017 The MDAnalysis Development Team and contributors
# (see the file AUTHORS for the full list of names)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# R. J. Gowers, M. Linke, J. Barnoud, T. J. E. Reddy, M. N. Melo, S. L. Seyler,
# D. L. Dotson, J. Domanski, S. Buchoux, I. M. Kenney, and O. Beckstein.
# MDAnalysis: A Python package for the rapid analysis of molecular dynamics
# simulations. In S. Benthall and S. Rostrup editors, Proceedings of the 15th
# Python in Science Conference, pages 102-109, Austin, TX, 2016. SciPy.
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#

"""\
Fitting transformations --- :mod:`MDAnalysis.transformations.fit`
=================================================================

Translate and rotates the coordinates of a given trajectory to align
a given AtomGroup to a reference structure.
    
"""
from __future__ import absolute_import

import numpy as np
from functools import partial

from ..analysis import align
from ..lib.util import get_weights
from ..lib.transformations import euler_from_matrix, euler_matrix

def alignto(ag, reference, weights=None):
    
    """Perform a spatial superposition by minimizing the RMSD.

    Spatially align the group of atoms `ag` to `reference` by
    doing a RMSD fit on `select` atoms.

    A detailed description on the way the fitting is performed can be found in
    :func:`MDAnalysis.analysis.align.alignto`
    
    Example
    -------
    
    ..code-block::python
    
        ag = u.select_atoms("protein")
        ref = mda.Universe("reference.pdb")
        transform = MDAnalysis.transformations.alignto(ag, ref, wheights="mass")
        u.trajectory.add_transformations(transform)

    Parameters
    ----------
    ag : Universe or AtomGroup
       structure to be aligned, a
       :class:`~MDAnalysis.core.groups.AtomGroup` or a whole
       :class:`~MDAnalysis.core.universe.Universe`
    reference : Universe or AtomGroup
       reference structure, a :class:`~MDAnalysis.core.groups.AtomGroup`
       or a whole :class:`~MDAnalysis.core.universe.Universe`
    weights : {"mass", ``None``} or array_like, optional
       choose weights. With ``"mass"`` uses masses as weights; with ``None``
       weigh each atom equally. If a float array of the same length as
       `ag` is provided, use each element of the `array_like` as a
       weight for the corresponding atom in `mobile`.

    Returns
    -------
    MDAnalysis.coordinates.base.Timestep
    
    """
    
    def wrapped(ts):
        align.alignto(ag, reference, weights=weights)
        
        return ts

    return wrapped


def fit_translation(ag, reference, plane=None, center_of="geometry"):

    """Translates a given AtomGroup so that its center of geometry/mass matches 
    the respective center of the given reference. A plane can be given by the
    user using the option `plane`, and will result in the removal of
    the translation motions of the AtomGroup over that particular plane.
    
    Example
    -------
    Removing the translations of a given AtomGroup `ag` on the XY plane by fitting 
    its center of mass to the center of mass of a reference `ref`:
    
    ..code-block::python
    
        ag = u.select_atoms("protein")
        ref = mda.Universe("reference.pdb")
        transform = MDAnalysis.transformations.fit_translation(ag, ref, plane="xy", center_of="mass")
        u.trajectory.add_transformations(transform)
    
    Parameters
    ----------
    ag : Universe or AtomGroup
       structure to translate, a
       :class:`~MDAnalysis.core.groups.AtomGroup` or a whole 
       :class:`~MDAnalysis.core.universe.Universe`
    reference : Universe or AtomGroup
       reference structure, a :class:`~MDAnalysis.core.groups.AtomGroup` or a whole 
       :class:`~MDAnalysis.core.universe.Universe`
    plane: str, optional
        used to define the plane on which the translations will be removed. Defined as a 
        string of the plane. Suported planes are yz, xz and xy planes.
    center_of: str, optional
        used to choose the method of centering on the given atom group. Can be 'geometry'
        or 'mass'. Default is "geometry".
    
    Returns
    -------
    MDAnalysis.coordinates.base.Timestep
    """
    
    if plane is not None:
        if plane not in ('xy', 'yz', 'xz'):
            raise ValueError('{} is not a valid plane'.format(plane))
        axes = {'yz' : 0, 'xz' : 1, 'xy' : 2}
        plane = axes[plane]
    try:
        if center_of == 'geometry':
            ref_center = partial(reference.atoms.center_of_geometry)
            ag_center = partial(ag.atoms.center_of_geometry)
        elif center_of == 'mass':
            ref_center = partial(reference.atoms.center_of_mass)
            ag_center = partial(ag.atoms.center_of_mass)
        else:
            raise ValueError('{} is not a valid argument for "center_of"'.format(center_of))
    except AttributeError:
        if center_of == 'mass':
            raise AttributeError('Either {} or {} is not an Universe/AtomGroup object with masses'.format(ag, reference))
        else:
            raise ValueError('Either {} or {} is not an Universe/AtomGroup object'.format(ag, reference))
    
    reference = np.asarray(ref_center(), np.float32)

    def wrapped(ts):
        center = np.asarray(ag_center(), np.float32)
        vector = reference - center
        if plane:
            vector[plane] = 0
        ts.positions += vector
        
        return ts
    
    return wrapped


def fit_rot_trans(ag, reference, plane=None, weights=None):
    """Perform a spatial superposition by minimizing the RMSD.

    Spatially align the group of atoms `ag` to `reference` by doing a RMSD
    fit on `select` atoms.
    
    This fit works as a way o remove translations and rotations of a given
    AtomGroup in a trajectory. A plane can be given using the flag `plane`
    so that only translations and rotations in that particular plane are
    removed. This is useful for protein-membrane systems to where the membrane
    must remain in the same orientation.
    
    Example
    -------
    Removing the translations and rotations of a given AtomGroup `ag` on the XY plane
    by fitting it to a reference `ref`, using the masses as weights for the RMSD fit.
    
    ..code-block::python
    
        ag = u.select_atoms("protein")
        ref = mda.Universe("reference.pdb")
        transform = MDAnalysis.transformations.fit_rot_trans(ag, ref, plane="xy", weights="mass")
        u.trajectory.add_transformations(transform)
    
    Parameter
    ---------
    ag : Universe or AtomGroup
       structure to translate, a
       :class:`~MDAnalysis.core.groups.AtomGroup` or a whole 
       :class:`~MDAnalysis.core.universe.Universe`
    reference : Universe or AtomGroup
       reference structure, a :class:`~MDAnalysis.core.groups.AtomGroup` or a whole 
       :class:`~MDAnalysis.core.universe.Universe`
    plane: str, optional
        used to define the plane on which the translations will be removed. Defined as a 
        string of the plane. Suported planes are "yz", "xz" and "xy" planes.
    weights : {"mass", ``None``} or array_like, optional
       choose weights. With ``"mass"`` uses masses as weights; with ``None``
       weigh each atom equally. If a float array of the same length as
       `ag` is provided, use each element of the `array_like` as a
       weight for the corresponding atom in `mobile`.
       
    Returns
    -------
    MDAnalysis.coordinates.base.Timestep
    """
    if plane is not None:
        if plane not in ('xy', 'yz', 'xz'):
            raise ValueError('{} is not a valid plane'.format(plane))
        axes = {'yz' : 0, 'xz' : 1, 'xy' : 2}
        plane = axes[plane]
    reference, ag = align.get_matching_atoms(reference.atoms, ag.atoms)
    weights = align.get_weights(reference.atoms, weights)
    ref_com = reference.atoms.center(weights)
    ref_coordinates = reference.atoms.positions - ref_com   
    def wrapped(ts):
        mobile_com = ag.atoms.center(weights)
        mobile_coordinates = ts.positions - mobile_com
        rotation, dump = align.rotation_matrix(mobile_coordinates, ref_coordinates, weights=weights)
        if plane:
            euler_angs = euler_from_matrix(rotation, axes='sxyz')
            euler_angs[plane] = 0
            rotation = euler_matrix(euler_angs[0], euler_angs[1], euler_angs[2], axes='sxyz')
        ts.positions = ts.positions + (ref_com - mobile_com)
        ts.positions = np.dot(ts.positions, rotation)
        
        return ts
    
    return wrapped
