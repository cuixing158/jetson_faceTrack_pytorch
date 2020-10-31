function outBox = makeSquare(bboxes)
% makeSquare    Make the bounding box square.
    
% Copyright 2019 The MathWorks, Inc.
    
    maxSide = max(bboxes(:, 3:4), [], 2);
    cx = bboxes(:, 1) + bboxes(:, 3)/2;
    cy = bboxes(:, 2) + bboxes(:, 4)/2;
    outBox = [cx - maxSide/2, cy - maxSide/2, maxSide, maxSide];
end