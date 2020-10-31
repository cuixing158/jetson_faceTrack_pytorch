function cropped = cropImage(im, bboxes, outSize)
% cropImage     Crop and resize image.

% Copyright 2019 The MathWorks, Inc.
    
    nBoxes = size(bboxes, 1);
    cropped = zeros(outSize, outSize, 3, nBoxes, 'like', im);
    for iBox = 1:nBoxes
        thisBox = bboxes(iBox, :);
        cropped(:,:,:,iBox) = imresize(imcrop(im, thisBox), [outSize, outSize]);
    end
    
end