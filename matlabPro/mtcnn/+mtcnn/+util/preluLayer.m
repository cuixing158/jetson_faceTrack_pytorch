classdef preluLayer < nnet.layer.Layer
    % Example custom PReLU layer.
    % Taken from "Define Custom Deep Learning Layer with Learnable
    % Parameters"
    
    %  Copyright 2020 The MathWorks, Inc.

    properties (Learnable)
        % Scaling coefficient
        Alpha
    end
    
    methods
        function layer = preluLayer(weights, name) 
            % layer = preluLayer(numChannels, name) creates a PReLU layer
            % for 2-D image input with numChannels channels and specifies 
            % the layer name.

            layer.Name = name;
            layer.Alpha = weights;
        end
        
        function Z = predict(layer, X)
            % Z = predict(layer, X) forwards the input data X through the
            % layer and outputs the result Z.
            Z = max(X,0) + layer.Alpha .* min(0,X);
        end
        
        function [dLdX, dLdAlpha] = backward(layer, X, ~, dLdZ, ~)
            dLdX = layer.Alpha .* dLdZ;
            dLdX(X>0) = dLdZ(X>0);
            dLdAlpha = min(0,X) .* dLdZ;
            dLdAlpha = sum(sum(dLdAlpha,1),2);
            
            % Sum over all observations in mini-batch.
            dLdAlpha = sum(dLdAlpha,4);
        end
    end
end