function x = prelu(x, params)
% prelu   Parameterized relu activation.

% Copyright 2019 The MathWorks, Inc.

    x = max(0, x) + params.*min(0, x);
    
end