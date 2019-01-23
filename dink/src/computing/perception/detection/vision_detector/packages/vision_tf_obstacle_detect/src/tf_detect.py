#!/usr/bin/env python

# ROS
import rospy

import cv2

from autoware_msgs.msg import DetectedObject,DetectedObjectArray

from sensor_msgs.msg import Image

from cv_bridge import CvBridge, CvBridgeError

from detector import Detector
import utils


class TFDetectNode(object):
    """docstring for PeopleObjectDetectionNode."""
    def __init__(self):
        super(TFDetectNode, self).__init__()

        # init the node
        rospy.init_node('tf_detect', anonymous=False)

        # Get the parameters
        (model_name, num_of_classes, label_file, camera_namespace, video_name,
            num_workers) \
        = self.get_parameters()

        # Create Detector
        self._detector = Detector(model_name, num_of_classes, label_file,
            num_workers)

        self._bridge = CvBridge()

        # Advertise the result of Object Detector
        self.pub_detections_data = rospy.Publisher('/detection/vision_objects', DetectedObjectArray, queue_size=1)
        # self.pub_detections_data = rospy.Publisher('/detections', DetectionArray, queue_size=1)
        # self.pub_detections_data = rospy.Publisher('/detections', DetectionArray, queue_size=1)

        # Advertise the result of Object Detector
        self.pub_detections_image = rospy.Publisher( '/result_ripe', Image, queue_size=1)
        # self.pub_detections_image = rospy.Publisher( '/object_detection/detections_image', Image, queue_size=1)





        self.sub_rgb = rospy.Subscriber('/image_raw',Image, self.rgb_callback, queue_size=1, buff_size=2**24)
        # USE CAMERA TEST
        # USE CAMERA TEST
        # USE CAMERA TEST
        # self.sub_rgb = rospy.Subscriber('usb_cam/image_raw',Image, self.rgb_callback, queue_size=1, buff_size=2**24)





        # spin
        rospy.spin()

    def read_from_video(self, video_name):
        """
        Applies object detection to a video

        Args:
            Name of the video with full path

        Returns:

        """

        cap = cv2.VideoCapture(video_name)

        while(cap.isOpened()):
            ret, frame = cap.read()

            if frame is not None:
                image_message = \
                    self._bridge.cv2_to_imgmsg(frame, "bgr8")

                self.rgb_callback(image_message)

            else:
                break

        cap.release()
        cv2.destroyAllWindows()

        print "Video has been processed!"

        self.shutdown()

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


    def shutdown(self):
        """
        Shuts down the node
        """
        rospy.signal_shutdown("See ya!")

    def rgb_callback(self, data):
        """
        Callback for RGB images
        """
        print('rgb_callback')

        try:
            # .publish(self._cv_bridge.cv2_to_imgmsg(image_np, "bgr8"))
            # Convert image to numpy array
            cv_image = self._bridge.imgmsg_to_cv2(data, "bgr8")

            # Detect
            (output_dict, category_index) = \
                self._detector.detect(cv_image)


            # Create the message
            msg,len = \
                utils.create_detection_aw_msg(\
                data, output_dict, category_index, self._bridge)


            # Draw bounding boxes
            image_np = \
                self._detector.visualize(cv_image, output_dict)



            # Publish the messages
            self.pub_detections_data.publish(msg)
            self.pub_detections_image.publish(self._bridge.cv2_to_imgmsg(image_np, "bgr8"))

        except CvBridgeError as e:
            print(e)

def main():
    """ main function
    """
    node = TFDetectNode()

if __name__ == '__main__':
    main()
