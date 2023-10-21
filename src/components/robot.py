from src import constants
from src.components.component import Component
from src.utilities import utils_urdf, utils_io


class Robot(Component):

    __slots__ = [
        "urdf_fpath"
    ]

    _type = constants.COMPONENT_TYPE_ROBOT

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.urdf_fpath = parameters.get("urdf_fpath", None)
        if self.urdf_fpath is not None:
            self.urdf_fpath = utils_io.validate_resource_filepath(fpath=self.urdf_fpath)

    def initialise(self, **kwargs):

        if self.urdf_fpath is None:
            return


        robot_blueprint = utils_urdf.load_urdf(fpath=self.urdf_fpath)

        g = 0

