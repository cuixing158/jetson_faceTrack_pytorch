function [probability, correction, landmarks] = onet(x, weights)
% onet  Apply the onet network to a batch of images.

% Copyright 2019 The MathWorks, Inc.

    for layer = 1:4
        weightName = sprintf("features_conv%d_weight", layer);
        biasName = sprintf("features_conv%d_bias", layer);
        x = dlconv(x, ...
            weights.(weightName), ...
            weights.(biasName));
        
        preluName = sprintf("features_prelu%d_weight", layer);
        x = mtcnn.util.prelu(x, weights.(preluName));
        
        if layer < 4
            if layer == 3
                kernel = 2;
            else
                kernel = 3;
            end
            if layer == 1
                % This padding is required to replicate the default padding
                % from the original Caffe implementation
                padding = [0, 0; 2, 2];
            else
                padding = 0;
            end
            x = maxpool(x, kernel, "Stride", 2, "Padding", padding);
        end
    end
    
    x = fullyconnect(x, weights.features_conv5_weight, weights.features_conv5_bias);
    % inference only so no dropout
    x = mtcnn.util.prelu(x, weights.features_prelu5_weight);
    
    probability = fullyconnect(x, weights.conv6_1_weight, weights.conv6_1_bias);
    correction = fullyconnect(x, weights.conv6_2_weight, weights.conv6_2_bias);
    landmarks = fullyconnect(x, weights.conv6_3_weight, weights.conv6_3_bias);
    probability = softmax(probability);
end
