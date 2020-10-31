function [probability, correction] = pnet(x, weights)
% pnet  Apply the pnet network to a batch of images.

% Copyright 2019 The MathWorks, Inc.

    for layer = 1:3
        weightName = sprintf("features_conv%d_weight", layer);
        biasName = sprintf("features_conv%d_bias", layer);
        x = dlconv(x, ...
            weights.(weightName), ...
            weights.(biasName));
        
        preluName = sprintf("features_prelu%d_weight", layer);
        x = mtcnn.util.prelu(x, weights.(preluName));
        
        if layer == 1
            x = maxpool(x, 2, "Stride", 2);
        end
    end
    
    probability = dlconv(x, weights.conv4_1_weight, weights.conv4_1_bias);
    correction = dlconv(x, weights.conv4_2_weight, weights.conv4_2_bias);
    probability = softmax(probability);

end