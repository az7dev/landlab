#! /usr/env/python

"""flow_director_to_one.py provides a private class to help create
FlowDirectors.

Provides the _FlowDirectorToOne component which makes sure all model
grid fields are set up correctly.
"""
import numpy as np

from landlab.components.flow_director.flow_director import _FlowDirector


class _FlowDirectorToOne(_FlowDirector):

    """Private class for creating components to calculate flow directions.

    This class is not meant to be used directly in modeling efforts. It
    inherits from the _FlowDirector class and builds on it to provide the
    functionality that all flow direction calculators need if they direct flow
    only to one nodes, as in steepest descent or D8 direction finding. It
    exists in contrast to the other intermediate flow director class
    _FlowDirectorToMany which provides equivalent functionality for flow
    direction algorithms such as D infinity or D trig that route flow from one
    cell to multiple nodes. As the primary difference between these two methods
    is the names of the fields they create and use, the primary function of
    this class is to create model grid fields.

    Specifically, it stores as ModelGrid fields:

    -  Node array of receivers (nodes that receive flow), or ITS OWN ID if
       there is no receiver: *'flow__receiver_node'*
    -  Node array of steepest downhill slopes:
       *'topographic__steepest_slope'*
    -  Node array containing ID of link that leads from each node to its
       receiver, or BAD_INDEX_VALUE if no link:
       *'flow__link_to_receiver_node'*
    -  Boolean node array of all local lows: *'flow__sink_flag'*

    The primary method of this class, :func:`run_one_step` is not implemented.

    Parameters
    ----------
    grid : ModelGrid
        A grid.
    surface : field name at node or array of length node
        The surface to direct flow across.

    Examples
    --------
    >>> from landlab import RasterModelGrid
    >>> from landlab.components.flow_director.flow_director_to_one import (
    ...     _FlowDirectorToOne,
    ... )
    >>> mg = RasterModelGrid((3, 3), xy_spacing=(1, 1))
    >>> mg.set_closed_boundaries_at_grid_edges(True, True, True, False)
    >>> _ = mg.add_field(
    ...     "topographic__elevation",
    ...     mg.node_x + mg.node_y,
    ...     at="node",
    ... )
    >>> fd = _FlowDirectorToOne(mg, "topographic__elevation")
    >>> fd.surface_values
    array([ 0.,  1.,  2.,  1.,  2.,  3.,  2.,  3.,  4.])
    >>> sorted(list(mg.at_node.keys()))
    ['flow__link_to_receiver_node',
     'flow__receiver_node',
     'flow__sink_flag',
     'topographic__elevation',
     'topographic__steepest_slope']
    """

    _name = "FlowDirectorToOne"

    _unit_agnostic = True

    _info = {
        "flow__link_to_receiver_node": {
            "dtype": int,
            "intent": "out",
            "optional": False,
            "units": "-",
            "mapping": "node",
            "doc": "ID of link downstream of each node, which carries the discharge",
        },
        "flow__receiver_node": {
            "dtype": int,
            "intent": "out",
            "optional": False,
            "units": "-",
            "mapping": "node",
            "doc": "Node array of receivers (node that receives flow from current node)",
        },
        "flow__sink_flag": {
            "dtype": bool,
            "intent": "out",
            "optional": False,
            "units": "-",
            "mapping": "node",
            "doc": "Boolean array, True at local lows",
        },
        "topographic__elevation": {
            "dtype": float,
            "intent": "in",
            "optional": True,
            "units": "m",
            "mapping": "node",
            "doc": "Land surface topographic elevation",
        },
        "topographic__steepest_slope": {
            "dtype": float,
            "intent": "out",
            "optional": False,
            "units": "-",
            "mapping": "node",
            "doc": "The steepest *downhill* slope",
        },
    }

    def __init__(self, grid, surface):
        """Initialize the _FlowDirectorTo_One class."""
        # run init for the inherited class

        super().__init__(grid, surface)
        self.initialize_output_fields()

        self._to_n_receivers = "one"
        # initialize new fields
        self._steepest_slope = grid.at_node["topographic__steepest_slope"]

        self._links_to_receiver = grid.at_node["flow__link_to_receiver_node"]
        if np.all(self._links_to_receiver == 0):
            self._links_to_receiver.fill(self._grid.BAD_INDEX)

        self._receiver = grid.at_node["flow__receiver_node"]
        if np.all(self._receiver == 0):
            self._receiver.fill(self._grid.BAD_INDEX)

    def run_one_step(self):
        """run_one_step is not implemented for this component."""
        raise NotImplementedError("run_one_step()")

    # set properties. These are the same for all DirectToOne Directors
    # Number of Node

    @property
    def links_to_receiver(self):
        """ID of link downstream of each node, which carries the discharge."""
        return self._links_to_receiver

    @property
    def node_receiving_flow(self):
        """Return the node id of the node receiving flow.

        Examples
        --------
        >>> from landlab import RasterModelGrid
        >>> from landlab.components import FlowDirectorSteepest
        >>> mg = RasterModelGrid((3, 3))
        >>> mg.set_closed_boundaries_at_grid_edges(True, True, True, False)
        >>> _ = mg.add_field(
        ...     "topographic__elevation",
        ...     mg.node_x + mg.node_y,
        ...     at="node",
        ... )
        >>> fd = FlowDirectorSteepest(mg, "topographic__elevation")
        >>> fd.run_one_step()
        >>> fd.node_receiving_flow
        array([0, 1, 2,
               3, 1, 5,
               6, 7, 8])
        """
        return self._grid["node"]["flow__receiver_node"]


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
