function outBboxes = applyCorrection(bboxes, correction)
% applyCorrection  Apply bounding box regression correction.

% Copyright 2019 The MathWorks, Inc.

    assert(all(bboxes(:, 3) == bboxes(:, 4)), ...
        "mtcnn:util:applyCorrection:badBox", ...
        "Correction assumes square bounding boxes.");

    scaledOffset = bboxes(:, 3).*correction;
    outBboxes = bboxes + scaledOffset;
    
end