classdef DagNetworkStrategy < handle
    
    properties (SetAccess=private)
        % Trained Dag networks
        Pnet
        Rnet
        Onet
        ExecutionEnvironment
    end
    
    methods
        function obj = DagNetworkStrategy(useGpu)
            if useGpu
                obj.ExecutionEnvironment = "gpu";
            else
                obj.ExecutionEnvironment = "cpu";
            end
        end
        
        function load(obj)
            % loadWeights   Load the network weights from file.
            obj.Pnet = importdata(fullfile(mtcnnRoot(), "weights", "dagPNet.mat"));
            obj.Rnet = importdata(fullfile(mtcnnRoot(), "weights", "dagRNet.mat"));
            obj.Onet = importdata(fullfile(mtcnnRoot(), "weights", "dagONet.mat"));
        end
        
        function [probability, correction] = applyPNet(obj, im)
            % need to use activations as we don't know what size it will be
            result = obj.Pnet.activations(im, "concat", ...
                "ExecutionEnvironment", obj.ExecutionEnvironment);
            
            probability = result(:,:,1:2,:);
            correction = result(:,:,3:end,:);
        end
        
        function [probs, correction] = applyRNet(obj, im)
            output = obj.Rnet.predict(im, "ExecutionEnvironment", obj.ExecutionEnvironment);
            
            probs = output(:,1:2);
            correction = output(:,3:end);
        end
        
        function [probs, correction, landmarks] = applyONet(obj, im)
            output = obj.Onet.predict(im, "ExecutionEnvironment", obj.ExecutionEnvironment);
            
            probs = output(:,1:2);
            correction = output(:,3:6);
            landmarks = output(:,7:end);
        end
        
    end
end