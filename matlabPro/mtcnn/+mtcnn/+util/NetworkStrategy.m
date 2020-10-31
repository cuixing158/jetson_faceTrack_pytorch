classdef (Abstract) NetworkStrategy < handle
    methods
        load(obj)
        pnet = getPNet(obj)
        [probs, correction] = applyRNet(obj, im)
        [probs, correction, landmarks] = applyONet(obj, im)
    end
end