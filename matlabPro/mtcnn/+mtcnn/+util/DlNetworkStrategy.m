classdef DlNetworkStrategy < handle
    
    properties (SetAccess=private)
        UseGPU
        % Weights for the networks
        PnetWeights
        RnetWeights
        OnetWeights
    end
    
    methods
        function obj = DlNetworkStrategy(useGpu)
            obj.UseGPU = useGpu;
        end
        
        function load(obj)
            % loadWeights   Load the network weights from file.
            obj.PnetWeights = load(fullfile(mtcnnRoot(), "weights", "pnet.mat"));
            obj.RnetWeights = load(fullfile(mtcnnRoot(), "weights", "rnet.mat"));
            obj.OnetWeights = load(fullfile(mtcnnRoot(), "weights", "onet.mat"));
            
            if obj.UseGPU
                obj.PnetWeights = dlupdate(@gpuArray, obj.PnetWeights);
                obj.RnetWeights = dlupdate(@gpuArray, obj.RnetWeights);
                obj.OnetWeights = dlupdate(@gpuArray, obj.OnetWeights);
            end
        end
        
        function [probability, correction] = applyPNet(obj, im)
            im = dlarray(im, "SSCB");
            
            [probability, correction] = mtcnn.pnet(im, obj.PnetWeights);
            
            probability = extractdata(gather(probability));
            correction = extractdata(gather(correction));
        end
        
        function [probs, correction] = applyRNet(obj, im)
            im = dlarray(im, "SSCB");
            
            [probs, correction] = mtcnn.rnet(im, obj.RnetWeights);
            
            probs = extractdata(probs)';
            correction = extractdata(correction)';
        end
        
        function [probs, correction, landmarks] = applyONet(obj, im)
            im = dlarray(im, "SSCB");
            
            [probs, correction, landmarks] = mtcnn.onet(im, obj.OnetWeights);
            
            probs = extractdata(probs)';
            correction = extractdata(correction)';
            landmarks = extractdata(landmarks)';
        end
        
    end
end