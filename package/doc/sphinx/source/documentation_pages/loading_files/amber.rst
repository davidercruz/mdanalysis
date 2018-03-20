.. _loading_amber:

###################################
Loading Amber files with MDAnalysis
###################################

MDAnalysis can read PRMTOP, NCDF and ascii coordinate and restart files from
Amber_.
Typically using NCDF as the trajectory format will give the best performance
as all other trajectory formats are ascii based.

.. _Amber: http://ambermd.org


.. _load_amber_top:

Loading Amber PRMTOP files
--------------------------

MDAnalysis reads `TOP format`_ files with an extension of ``TOP``,
``PRMTOP`` or ``PARM7``.
The below table shows the relationship between Amber flags and the attribute
created in MDAnalysis:
The ``type_indices`` attribute is unique to Amber formats and is
an *integer* representation of the atom type, rather than the
typical string representation found throughout MDAnalysis.

.. table:: Mapping of Amber flags to MDAnalysis attributes

  +-----------------+----------------------+
  | AMBER flag      | MDAnalysis attribute |
  +=================+======================+
  | ATOM_NAME       | names                |
  +-----------------+----------------------+
  | CHARGE          | charges              |
  +-----------------+----------------------+
  | ATOMIC_NUMBER   | elements             |
  +-----------------+----------------------+
  | MASS            | masses               |
  +-----------------+----------------------+
  | ATOM_TYPE_INDEX | type_indices         |
  +-----------------+----------------------+
  | AMBER_ATOM_TYPE | types                |
  +-----------------+----------------------+
  | RESIDUE_LABEL   | resnames             |
  +-----------------+----------------------+
  | RESIDUE_POINTER | residues             |
  +-----------------+----------------------+

.. note::

   The Amber charge is converted to electron charges as used in
   MDAnalysis and other packages. To get back Amber charges, multiply
   by 18.2223.

For implementation details, see
:mod:`MDAnalysis.topology.TOPParser`.

.. _`TOP format`: http://ambermd.org/formats.html#topo.cntrl

.. _load_amber_ncdf:

Loading Amber NCDF files
------------------------

Pecularities of Amber NCDF files


.. _load_amber_trj:

Loading TRJ files
-----------------

All about loading Amber ascii TRJ files

.. _load_amber_restart:

Loading Amber restart files
---------------------------

All about loading Amber restart files
