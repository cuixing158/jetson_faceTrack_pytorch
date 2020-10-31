function scales = calculateScales(im, minSize, maxSize, defaultScale, pyramidScale)
    % calculateScales Compute image scales for a given size range.
    %
    %   Args:
    %       im              Input image
    %       minSize         Minimum pixel size for detection
    %       maxSize         Maximum pixel size for detection
    %       defaultScale    Pixel size of proposal network
    %       pyramidScale    Scale factor for image pyramid this must be
    %                       greater than 1 (optional, default = sqrt(2))
    %
    %   Returns:
    %       scales          1xn row vector of calculated pyramid scales
    
    % Copyright 2019 The MathWorks, Inc.
    
    if nargin < 5
        pyramidScale = sqrt(2);
    else
        assert(pyramidScale > 1, ...
            "mtcnn:util:calculateScales:badScale", ...
            "PyramidScale must be >1 but it was %f", pyramidScale);
    end
    
    imSize = size(im);
    
    % if maxSize is empty assume the smallest image dimension
    if isempty(maxSize)
        maxSize = min(imSize(1:2));
    end
    
    % Calculate min and max scaling factors required
    minScale = minSize/defaultScale;
    maxScale = maxSize/defaultScale;
    
    % Round to multiples or sqrt(2)
    alpha = floor(log(maxScale/minScale)/log(pyramidScale));
    scales = minScale.*pyramidScale.^(0:alpha);
end