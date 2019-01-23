#!/usr/bin/env python

# ROS
import rospy

import cv2

from sensor_msgs.msg import Image

from cv_bridge import CvBridge, CvBridgeError

from detector import Detector

import utils

from tf_server.srv import TF_detect




class Tensorflow_detect_node(object):

    def __init__(self):
        super(Tensorflow_detect_node, self).__init__()

        # init the node
        rospy.init_node('tensorflow_detect_node', anonymous=False)



        (model_name, num_of_classes, label_file, camera_namespace, video_name,
         num_workers) \
            = self.get_parameters()

        # Create Detector
        self._detector = Detector(model_name, num_of_classes, label_file,
                                  num_workers)


        self._bridge = CvBridge()


        self.sub_rgb = rospy.Subscriber('usb_cam/image_raw',Image, self.rgb_callback, queue_size=1, buff_size=2**24)
        self.pub_detections_image = rospy.Publisher('/result_ripe', Image, queue_size=1)
        # spin
        rospy.spin()


    def get_parameters(self):
        """
        Gets the necessary parameters from parameter server

        Args:

        Returns:
        (tuple) (model name, num_of_classes, label_file)

        """

        model_name  = rospy.get_param("~model_name")
        num_of_classes  = rospy.get_param("~num_of_classes")
        label_file  = rospy.get_param("~label_file")
        camera_namespace  = 'usb_cam/image_raw'
        # camera_namespace  = rospy.get_param("~camera_namespace")
        video_name = rospy.get_param("~video_name")
        num_workers = rospy.get_param("~num_workers")

        return (model_name, num_of_classes, label_file, \
                camera_namespace, video_name, num_workers)

    def rgb_callback(self, data):


        rospy.wait_for_service('tf_detect_request')

        try:
            tensorflow_detect = rospy.ServiceProxy('tf_detect_request', TF_detect)
            resp1 = tensorflow_detect(data)
            print 'resp1.res '+str(resp1.res)




            cv_image = self._bridge.imgmsg_to_cv2(data, "bgr8")
            (output_dict, category_index) = self._detector.detect(cv_image)
            image_np = self._detector.visualize(cv_image, output_dict)
            self.pub_detections_image.publish(self._bridge.cv2_to_imgmsg(image_np, "bgr8"))




        except rospy.ServiceException, e:
            print "Service call failed: %s" % e



def main():
    """ main function
    """
    node = Tensorflow_detect_node()

if __name__ == '__main__':
    main()
