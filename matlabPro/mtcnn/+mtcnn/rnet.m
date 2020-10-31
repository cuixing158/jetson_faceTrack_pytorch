function [probability, correction] = rnet(x, weights)
% rnet  Apply the rnet network to a batch of images.

% Copyright 2019 The MathWorks, Inc.

    for layer = 1:3
        weightName = sprintf("features_conv%d_weight", layer);
        biasName = sprintf("features_conv%d_bias", layer);
        x = dlconv(x, ...
            weights.(weightName), ...
            weights.(biasName));
        
        preluName = sprintf("features_prelu%d_weight", layer);
        x = mtcnn.util.prelu(x, weights.(preluName));
        
        if layer == 1 || layer == 2
            if layer == 1
                % This padding is required to replicate the default padding
                % from the original Caffe implementation
                padding = [0, 0; 2, 2];
            else
                padding = 0;
            end
            x = maxpool(x, 3, "Stride", 2, "Padding", padding);
        end
    end
    
    nBatch = size(x,4);
    x = permute(stripdims(x), [4, 1, 2, 3]);
    x = dlarray(reshape(x, nBatch, []), "BC");

    x = fullyconnect(x, weights.features_conv4_weight, weights.features_conv4_bias);
    x = mtcnn.util.prelu(x, weights.features_prelu4_weight);
    probability = fullyconnect(x, weights.conv5_1_weight, weights.conv5_1_bias);
    correction = fullyconnect(x, weights.conv5_2_weight, weights.conv5_2_bias);
    probability = softmax(probability);
end