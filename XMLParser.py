#!usr/bin/env python

import xml.etree.ElementTree as ET
import farmer_log
from os import path

class XMLParser:
    """
    XMLParser class definition
    Attributes:
        _file_path            : xml file path
        _gpu_model             : GPU Mode
        _cuda_version         : Cude Version
        _cudnn_version        : Cudnn Version
        _topology_model_type  : Topoloy Model Type
        _framework            : Frame Type
        _batch_size           : Batch Size
        _dataSet              : Ohter Dataset
    """

    def __init__(self, filePath = None):
        self._file_path           = filePath
        self._gpu_model            = ""
        self._cuda_version        = ""
        self._cuda_version_string = ""
        self._cudnn_version       = ""
        self._cudnn_version_string = ""
        self._topology_model_type = ""
        self._framework           = ""
        self._batch_size          = ""
        self._tenseflow_installed = 0
        self._caffe_installed     = 0
        self._dataSet             = ""

    def set_file_path(self, file_path):
        self._file_path = file_path

    def parse(self):
        if not path.isfile(self._file_path):
            farmer_log.error("The xml file doesn't exist.")
            return

        tree = ET.parse(self._file_path)
        root = tree.getroot()
        self._gpu_model             = getAttr(root, "GPUModel")
        self._cuda_version         = float(getAttr(root, "CudaVersion"))
        self._cuda_version_string  = getAttr(root, "CudaVersionString")
        self._cudnn_version        = float(getAttr(root, "CudnnVersion"))
        self._cudnn_version_string = getAttr(root, "CudnnVersionString")
        self._topology_model_type  = getAttr(root, "TopologyMode")
        self._framework            = getAttr(root, "Framework")
        self._batch_size           = getAttr(root, "BatchSize")
        self._tenseflow_installed  = int(getAttr(root, "TensorflowInstalled"))
        self._caffe_installed      = int(getAttr(root, "CaffeInstalled"))
        self._dataSet              = getAttr(root, "DataSet")


    def generate_xml(self, gpu_model, batch_size, iterations, topology, cuda, cudnn, framework):
        """
        """

    def getGPUMode(self):
        return self._gpu_model

    def getCudeVersion(self):
        return self._cuda_version

    def getCudeVersionString(self):
        return self._cuda_version_string

    def getCudnnVersion(self):
        return self._cudnn_version

    def getCudnnVersionString(self):
        return self._cudnn_version_string

    def getTopologyModeType(self):
        return self._topology_model_type

    def getFramework(self):
        return self._framework

    def getBatchSize(self):
        return self._batch_size

    def getDataSet(self):
        return self._dataSet

    def is_tenseflow_installed(self):
        return self._tenseflow_installed

    def is_caffe_installed(self):
        return self._caffe_installed

def getAttr(tree, name):
    path = 'DockerInfo[@name="%s"]' % name
    elem = tree.findall(path)
    return elem[0].attrib["value"]

if __name__ == "__main__":
    parser = XMLParser("XXX")
    parser.parse()

    parser = XMLParser("DockerConfig.xml")
    parser.parse()
    print parser.getGPUMode() + "\n" \
    + str(parser.getCudeVersion()) + '\n' \
    + str(parser.getCudnnVersion()) + '\n' \
    + parser.getCudeVersionString() + '\n' \
    + parser.getCudnnVersionString() + '\n' \
    + parser.getTopologyModeType() + '\n' \
    + parser.getFramework() + '\n' \
    + parser.getBatchSize() + '\n' \
    + parser.getDataSet() + '\n'

