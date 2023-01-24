import ctk
import numpy as np
import vtk
import logging
import qt
import slicer
from slicer.ScriptedLoadableModule import *


class ProgrammingAssignmentPauloMedeiros(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:

    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        applicant_name = "Paulo Medeiros"
        self.parent.title = "Programming Assignment: {}".format(applicant_name)
        self.parent.categories = ["Programming Assignment"]
        self.parent.dependencies = []
        self.parent.contributors = [applicant_name]
        self.parent.helpText = ""
        self.parent.acknowledgementText = ""


class ProgrammingAssignmentPauloMedeirosWidget(ScriptedLoadableModuleWidget):

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.logic = ProgrammingAssignmentPauloMedeirosLogic()

        # Instantiate and connect widgets ...

        #
        # Parameters Area
        #
        parameters_collapsible_button = ctk.ctkCollapsibleButton()
        parameters_collapsible_button.text = "Parameters"
        self.layout.addWidget(parameters_collapsible_button)

        # Layout within the dummy collapsible button
        parameters_form_layout = qt.QFormLayout(parameters_collapsible_button)

        #
        # input volume selector
        #
        self.input_selector = slicer.qMRMLNodeComboBox()
        self.input_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.input_selector.selectNodeUponCreation = True
        self.input_selector.addEnabled = False
        self.input_selector.removeEnabled = False
        self.input_selector.noneEnabled = False
        self.input_selector.showHidden = False
        self.input_selector.showChildNodeTypes = False
        self.input_selector.setMRMLScene(slicer.mrmlScene)
        self.input_selector.setToolTip("Pick the input to the algorithm.")
        parameters_form_layout.addRow("Input Volume: ", self.input_selector)

        #
        # output volume selector
        #
        self.output_selector = slicer.qMRMLNodeComboBox()
        self.output_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.output_selector.selectNodeUponCreation = True
        self.output_selector.addEnabled = True
        self.output_selector.renameEnabled = True
        self.output_selector.removeEnabled = True
        self.output_selector.noneEnabled = False
        self.output_selector.showHidden = False
        self.output_selector.showChildNodeTypes = False
        self.output_selector.setMRMLScene(slicer.mrmlScene)
        self.output_selector.setToolTip("Pick the output to the algorithm.")
        parameters_form_layout.addRow("Output Volume: ", self.output_selector)

        #
        # threshold value
        #
        self.image_threshold_slider_vidget = ctk.ctkSliderWidget()
        self.image_threshold_slider_vidget.singleStep = 0.01
        self.image_threshold_slider_vidget.minimum = 0
        self.image_threshold_slider_vidget.maximum = 1
        self.image_threshold_slider_vidget.value = 0.5
        parameters_form_layout.addRow("Image threshold", self.image_threshold_slider_vidget)

        #
        # Apply Button
        #
        self.apply_button = qt.QPushButton("Apply")
        self.apply_button.toolTip = "Run the algorithm?"
        self.apply_button.enabled = False
        parameters_form_layout.addRow(self.apply_button)

        # connections: button and arguments
        self.apply_button.connect('clicked()', self.onApply)
        self.input_selector.connect('currentNodeChanged(vtkMRMLNode*)', self.onNodeSelectionChanged)
        self.output_selector.connect('currentNodeChanged(vtkMRMLNode*)', self.onNodeSelectionChanged)

        # Add vertical spacer
        self.layout.addStretch(1)

    def onApply(self):
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            
            # Lock GUI
            self.apply_button.text = "Working..."
            self.apply_button.setEnabled(False)
            slicer.app.processEvents()

            # Binarize input volume and save it at output volume
            self.logic.run(
                self.input_selector.currentNode(),
                self.output_selector.currentNode(),
                self.image_threshold_slider_vidget.value
            )

            # Displaying created volume
            slicer.util.setSliceViewerLayers(background = self.output_selector.currentNode())
            slicer.util.resetSliceViews()

        # Unlock GUI
        self.apply_button.setEnabled(True)
        self.apply_button.text = "Apply"

    def onNodeSelectionChanged(self):
        # Front-end validator of input
        nodes_not_none = (self.input_selector.currentNode() is not None and
                            self.output_selector.currentNode() is not None)

        nodes_not_same = (self.input_selector.currentNode().GetID() !=
                            self.output_selector.currentNode().GetID())

        self.apply_button.enabled = nodes_not_none and nodes_not_same

    def cleanup(self):
        pass


class ProgrammingAssignmentPauloMedeirosLogic(ScriptedLoadableModuleLogic):

    def has_image_data(self, volume_node):
        """Checks volume is defined and present image data"""
        if not volume_node:
            logging.debug("has_image_data failed: no volume node")
            return False
        if volume_node.GetImageData() is None:
            logging.debug("has_image_data failed: no image data in volume node")
            return False
        return True

    def is_valid_input_output_data(self, input_volume_node, output_volume_node):
        """Validates input and output"""

        if not self.has_image_data(input_volume_node):
            slicer.util.errorDisplay("Input volume is ill-defined")
            return False

        if not output_volume_node:
            slicer.util.errorDisplay("No output volume node defined")
            logging.debug("is_valid_input_output_data failed: no output volume node defined")
            return False

        if input_volume_node.GetID() == output_volume_node.GetID():
            slicer.util.errorDisplay("Input volume is the same as output volume. Choose a different output volume.")
            logging.debug(
                "is_valid_input_output_data failed: input and output volume is the same. Create a new volume for output to avoid this error."
            )
            return False
        return True

    def is_valid_threshold(self, threshold):
        """Validates threshold value"""
        if threshold < 0 or threshold > 1:
            logging.debug("Invalid threshold value: outside of range [0;1]")
            return False
        return True

    def run(self, input_volume, output_volume, image_threshold):
        """Run the actual algorithm"""

        if not self.is_valid_input_output_data(input_volume, output_volume):
            return False
        
        if not self.is_valid_threshold(image_threshold):
            slicer.util.errorDisplay("Invalid threshold value for binary segmentation")
            return False

        # Create an empty image volume w/ same dimenions as input, filled with fillVoxelValue
        voxelType = vtk.VTK_UNSIGNED_CHAR
        output_image = vtk.vtkImageData()
        output_image.SetDimensions(input_volume.GetImageData().GetDimensions())
        output_image.AllocateScalars(voxelType, 1)
        output_image.GetPointData().GetScalars().Fill(0)

        # Set volume node image data and minors
        output_volume.SetAndObserveImageData(output_image)
        output_volume.CreateDefaultDisplayNodes()
        output_volume.CreateDefaultStorageNode()

        # Compute threshold value based on input range
        input_range = input_volume.GetImageData().GetScalarRange()
        threshold_value = input_range[0] + (input_range[1] - input_range[0]) * image_threshold

        # Apply threshold. Modify (to 1) only masked pixels
        threshold_mask = slicer.util.arrayFromVolume(input_volume) > threshold_value
        slicer.util.arrayFromVolume(output_volume)[threshold_mask] = 1

        # Notify slicer it is completed
        output_volume.Modified()

        return True


class ProgrammingAssignmentPauloMedeirosTest(ScriptedLoadableModuleTest):
    """This is the test case for your scripted module.

    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_Threshold()

    def test_Threshold(self):
        self.delayDisplay("Starting test_Threshold")

        import SampleData
        self.delayDisplay("Load source volume")

        input_volume = SampleData.downloadSample('MRHead')
        output_volume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", 'test_node')

        segStatLogic = ProgrammingAssignmentPauloMedeirosLogic()
        
        # Invalid threshold args
        segStatLogic.run(input_volume, output_volume, -1)
        segStatLogic.run(input_volume, output_volume, 1.1)

        # Invalid volume args
        segStatLogic.run(None, None, 0.5)
        segStatLogic.run(None, output_volume, 0.5)
        segStatLogic.run(input_volume, None, 0.5)
        segStatLogic.run(input_volume, input_volume, 0.5)

        # Correct arguments for binary thresholding
        import random
        for _ in range(10):
            segStatLogic.run(input_volume, output_volume, random.random())
            output_array = slicer.util.arrayFromVolume(output_volume)
            output_values = np.unique(output_array)
            assert(list(output_values) == [0, 1])
            
        self.delayDisplay('test_Threshold passed!')