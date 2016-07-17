#!usr/bin/env python
import os
import workload
from xml_parser import *
from MySql_wrapper import Mysql_wrapper
from cmd_generator import *
from workload import Caffe_Workload
import pandas
import cmd_generator
from docker_control import Docker_Monitor
from gpu_control import *

class requests(object): 
    
    def __init__(self, gpuid, topologies, iterations, batch_size):
        self.gpuid = gpuid
        self.topologies = topologies
        self.iterations = iterations
        self.batch_size = batch_size 
        self.iterations = iterations
        self.batch_size = batch_size

class Task_Scheduler(object):

    def __init__(self):
        self.sql_wrapper = Mysql_wrapper('localhost', 'root', 'tracing', 'animations')
        self.docker_control = Docker_Monitor()
        self.gpu_monitor = GPUMonitor()
        self.gpu_monitor.init_local_gpu_lists()
        self.gpu_monitor.register_listener(self)
        self.requests = [] 

    def prepare_env(self):
        self.sql_wrapper.init_database()
        self.docker_control.get_local_images(self.sql_wrapper)

    def build_image(self):
        pass

    def parse_new_request_from_xml(self, filepath):
        xml_parser = XMLParser(filepath)
        config = xml_parser.parse_xml()
        gpu_device = self.gpu_monitor.get_gpu_from_model(config['gpu_model'])
        if gpu_device is None:
            farmer_logger.error('Internal Fatal Error, Wrong GPU Model Name')
            raise Exception('Internal Fatal Error')
        config['gpu_id'] = gpu_device.gpuid
        config['gpu_device'] = gpu_device            
        return config
 
    def assign_request(self, filepath):
        """
            scheduler tries to assign one request to one specified GPU
        """
        config = self.parse_new_request_from_xml(filepath)
        self.requests.append(config)
        if self.test_start(config):
            self.requests.remove(config) 
        
    def test_start(self, config):
        index = self.docker_control.get_image_index(config['cuda_string'], config['cudnn_string'], config['caffe'], config['tensorflow'])
        if index == -1:
            # TODO
            self.build_image()
            # TODO
            # docker control inert docker_image_info into database
            index = self.docker_control.get_image_index(config['cuda_string'], config['cudnn_string'], config['caffe'], config['tensorflow'])
        #gpuid = config['gpu_id'] 
        gpuid = 1
        image = self.docker_control.get_image(index)
        container = get_random_container()
        execute(run_docker(container, image.repository, image.tag))
        test_workload = Caffe_Workload(container)
        test_workload.copy()
        test_workload.run_batch(config['topology'], config['iterations'], config['batch_size'], gpuid)
        execute(stop_docker(container))
        return True

if __name__ == "__main__":
    scheduler = Task_Scheduler()
    scheduler.build_image()
    scheduler.prepare_env()
    scheduler.assign_request('/tmp/1.xml')
