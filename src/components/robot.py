from src import constants
from src.components.component import Component
from src.utilities import utils_urdf, utils_mjcf, utils_io


class Robot(Component):

    __slots__ = [
        "urdf_fpath",
        "mjcf_fpath"
    ]

    _type = constants.COMPONENT_TYPE_ROBOT

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.urdf_fpath = parameters.get("urdf_fpath", None)
        self.mjcf_fpath = parameters.get("mjcf_fpath", None)

    def initialise(self, **kwargs):

        if self.urdf_fpath is not None:
            self.urdf_fpath = utils_io.validate_resource_filepath(fpath=self.urdf_fpath)
            urdf_blueprint = utils_urdf.load_urdf(xml_fpath=self.urdf_fpath)

        if self.mjcf_fpath is not None:
            self.mjcf_fpath = utils_io.validate_resource_filepath(fpath=self.mjcf_fpath)
            mjcf_blueprint = utils_mjcf.load_mjcf(xml_fpath=self.mjcf_fpath)

        g = 0

