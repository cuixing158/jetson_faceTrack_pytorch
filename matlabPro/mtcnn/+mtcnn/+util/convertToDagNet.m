function net = convertToDagNet(stage)
    
    warnId = "deep:functionToLayerGraph:Placeholder";
    warnState = warning('off', warnId);
    restoreWarn = onCleanup(@() warning(warnState));
    
    switch stage
        case "p"
            inputSize = 12;
            nBlocks = 3;
            finalConnections = [sprintf("conv_%d", nBlocks), sprintf("prelu_%d", nBlocks)];
            catConnections = ["sm_1", "conv_5"];
        case "r"
            inputSize = 24;
            nBlocks = 4;
            finalConnections = [sprintf("prelu_%d", nBlocks-1), "fc_1";
                                "fc_1", sprintf("prelu_%d", nBlocks)];
            catConnections = ["sm_1", "fc_3"];
        case "o"
            inputSize = 48;
            nBlocks = 5;
            finalConnections = ["fc_1", sprintf("prelu_%d", nBlocks)];
            catConnections = ["sm_1", "fc_3", "fc_4"];
        otherwise
            error("mtcnn:convertToDagNet:unknownStage", ...
            "Stage '%s' is not recognised", stage)
    end

    matFilename = strcat(stage, "net.mat");
    weightsFile = load(fullfile(mtcnnRoot, "weights", matFilename));
    input = dlarray(zeros(inputSize, inputSize, 3, "single"), "SSCB");
    
    switch stage
        case "p"
            netFunc = @(x) mtcnn.pnet(x, weightsFile);
            [a, b] = netFunc(input);
            output = cat(3, a, b);
        case "r"
            netFunc = @(x) mtcnn.rnet(x, weightsFile);
            [a, b] = netFunc(input);
            output = cat(1, a, b);
        case "o"
            netFunc = @(x) mtcnn.onet(x, weightsFile);
            [a, b, c] = netFunc(input);
            output = cat(1, a, b, c);
    end
    
    lgraph = functionToLayerGraph(netFunc, input);
    placeholders = findPlaceholderLayers(lgraph);
    lgraph = removeLayers(lgraph, {placeholders.Name});

    for iPrelu = 1:nBlocks
        name = sprintf("prelu_%d", iPrelu);
        weightName = sprintf("features_prelu%d_weight", iPrelu);
        if iPrelu ~= nBlocks
            weights = weightsFile.(weightName);
        else
            weights = reshape(weightsFile.(weightName), 1, 1, []);
        end
        prelu = mtcnn.util.preluLayer(weights, name);
        lgraph = replaceLayer(lgraph, sprintf("plus_%d", iPrelu), prelu, "ReconnectBy", "order");

        if iPrelu ~= nBlocks
            lgraph = connectLayers(lgraph, sprintf("conv_%d", iPrelu), sprintf("prelu_%d", iPrelu));
        else
            % need to make different connections at the end of the
            % repeating blocks
            for iConnection = 1:size(finalConnections, 1)
                lgraph = connectLayers(lgraph, ...
                    finalConnections(iConnection, 1), ...
                    finalConnections(iConnection, 2));
            end

        end
    end

    lgraph = addLayers(lgraph, imageInputLayer([inputSize, inputSize, 3], ...
                                "Name", "input", ...
                                "Normalization", "none"));
    lgraph = connectLayers(lgraph, "input", "conv_1");

    lgraph = addLayers(lgraph, concatenationLayer(3, numel(catConnections), "Name", "concat"));
    for iConnection = 1:numel(catConnections)
        lgraph = connectLayers(lgraph, ...
                                catConnections(iConnection), ...
                                sprintf("concat/in%d", iConnection));
    end
    lgraph = addLayers(lgraph, regressionLayer("Name", "output"));
    lgraph = connectLayers(lgraph, "concat", "output");

    net = assembleNetwork(lgraph);
    result = net.predict(zeros(inputSize, inputSize, 3, "single"));

    difference = extractdata(sum(output - result', "all"));
    
    assert(difference < 1e-6, ...
        "mtcnn:convertToDagNet:outputMismatch", ...
        "Outputs of function and dag net do not match")
end