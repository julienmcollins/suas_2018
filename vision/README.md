# UAS at UCLA 2018 Drone Code: Vision
Code used to manage our vision system and process images to locate targets
while surveying a field.

### How is vision organized
 * Photographer
    * Interface with camera (trigger shutter/control zoom/etc)
    * Control gimbal
    * Generating simulated images for testing
 * Segmenter
    * Find areas of interest in the frames that we have collected
    * Crop out these sections in preparation for the classification stage
    * Match GPS coordinates to each segment based on camera specs & altitude
 * Classifier
    * Filter out segments that don't contain a target
    * Determine shape/letter/shape color/letter color of targets
    * Feedback from a real person about correctness (for additional training)

### Stuff used to make this work
 * [OpenCV](https://github.com/opencv/opencv) for image filtering/segmentation
 * [Tensorflow](https://github.com/tensorflow/tensorflow) for classification
