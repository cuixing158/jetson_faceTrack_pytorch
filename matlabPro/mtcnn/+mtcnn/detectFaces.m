function [bboxes, scores, landmarks] = detectFaces(im, varargin)
% detectFaces   Use a pretrained model to detect faces in an image.
%
%   Args:
%       im  - RGB input image for detection
%
%   Returns:
%       bbox        - nx4 array of face bounding boxes in the 
%                   format [x, y, w, h]
%       scores      - nx1 array of face probabilities
%       landmarks   - nx5x2 array of facial landmarks
%
%   Name-Value pairs:
%       detectFaces also takes the following optional Name-Value pairs:
%            - MinSize              - Approx. min size in pixels
%                                     (default=24)
%            - MaxSize              - Approx. max size in pixels
%                                     (default=[])
%            - PyramidScale         - Pyramid scales for region proposal
%                                     (default=sqrt(2))
%            - ConfidenceThresholds - Confidence threshold at each stage of detection
%                                     (default=[0.6, 0.7, 0.8])
%            - NmsThresholds        - Non-max suppression overlap thresholds
%                                     (default=[0.5, 0.5, 0.5])
%            - UseGPU               - Use GPU for processing or not
%                                     (default=false)
%            - UseDagNet            - Use DAGNetwork for prediction (for
%                                     compatibility with R2019a)
%                                     (default=false R2019b+, =true R2019a)
% 
%   Note:
%       The 5 landmarks detector are in the order:
%           - Left eye, right eye, nose, left mouth corner, right mouth corner
%       The final 2 dimensions correspond to x and y co-ords.
%
%   See also: mtcnn.Detector.detect

% Copyright 2019 The MathWorks, Inc.

    detector = mtcnn.Detector(varargin{:});
    [bboxes, scores, landmarks] = detector.detect(im);
end