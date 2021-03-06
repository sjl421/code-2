"""A VTK file reader object.

"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005-2008, Enthought, Inc.
# License: BSD Style.

# Standard library imports.
from os.path import basename

# Enthought library imports.
from enthought.traits.api import Instance
from enthought.tvtk.api import tvtk

# Local imports.
from enthought.mayavi.core.pipeline_info import (PipelineInfo, 
        get_tvtk_dataset_name)
from vtk_xml_file_reader import VTKXMLFileReader 


########################################################################
# `VTKFileReader` class
########################################################################
class VTKFileReader(VTKXMLFileReader):

    """A VTK file reader.  This does not handle the new XML file
    format but only the older format.  The reader supports all the
    different types of data sets.  This reader also supports a time
    series.
    """

    # The version of this class.  Used for persistence.
    __version__ = 0

    # The VTK data file reader.
    reader = Instance(tvtk.DataSetReader, args=(),
                      kw={'read_all_scalars':True, 
                          'read_all_vectors': True,
                          'read_all_tensors': True,
                          'read_all_fields': True} )    

    # Information about what this object can produce.
    output_info = PipelineInfo(datasets=['any'], 
                               attribute_types=['any'],
                               attributes=['any'])

    ######################################################################
    # Non-public interface
    ######################################################################
    def _file_path_changed(self, fpath):
        value = fpath.get()
        if len(value) == 0:
            self.name = 'No VTK file'
            return
        else:
            self.reader.file_name = value
            self.update()
            
            # Setup the outputs by resetting self.outputs.  Changing
            # the outputs automatically fires a pipeline_changed
            # event.
            try:
                n = self.reader.number_of_outputs
            except AttributeError: # for VTK >= 4.5
                n = self.reader.number_of_output_ports
            outputs = []
            for i in range(n):
                outputs.append(self.reader.get_output(i))
            self.outputs = outputs

            # FIXME: Only the first output goes through the assign
            # attribute filter.
            aa = self._assign_attribute
            aa.input = outputs[0]        
            outputs[0] = aa.output
            self.update_data()

            self.outputs = outputs

            # FIXME: The output info is only based on the first output.
            self.output_info.datasets = [get_tvtk_dataset_name(outputs[0])]

            # Change our name on the tree view
            self.name = self._get_name()

    def _get_name(self):
        """ Gets the name to display on the tree view.
        """
        fname = basename(self.file_path.get())
        ret = "VTK file (%s)"%fname
        if len(self.file_list) > 1:
            ret += " (timeseries)"
        if '[Hidden]' in self.name:
            ret += ' [Hidden]'

        return ret

