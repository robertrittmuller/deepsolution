//<![CDATA[

// a few things don't have var in front of them - they update already existing variables the game needs
lanesSide = 6;
patchesAhead = 35;
patchesBehind = 10;
trainIterations = 150000;

// the number of other autonomous vehicles controlled by your network
otherAgents = 0; // max of 10

var num_inputs = (lanesSide * 2 + 1) * (patchesAhead + patchesBehind);
var num_actions = 5;
var temporal_window = 0;
var network_size = num_inputs * temporal_window + num_actions * temporal_window + num_inputs;

var layer_defs = [];
    layer_defs.push({
    type: 'input',
    out_sx: 1,
    out_sy: 1,
    out_depth: network_size
});
layer_defs.push({
    type: 'fc',
    num_neurons: 30,
    activation: 'tanh'
});
layer_defs.push({
    type: 'fc',
    num_neurons: 14,
    activation: 'tanh'
});
layer_defs.push({
    type: 'fc',
    num_neurons: 14,
    activation: 'tanh'
});
layer_defs.push({
    type: 'fc',
    num_neurons: 30,
    activation: 'tanh'
});
layer_defs.push({
    type: 'regression',
    num_neurons: num_actions
});

var tdtrainer_options = {
    learning_rate: 0.01,
    momentum: 0.01,
    batch_size: 96,
    l2_decay: 0.01
};

var opt = {};
opt.temporal_window = temporal_window;
opt.experience_size = 30000;
opt.start_learn_threshold = 500;
opt.gamma = 0.96;
opt.learning_steps_total = trainIterations;
opt.learning_steps_burnin = 500;
opt.epsilon_min = 0.01;
opt.epsilon_test_time = 0.0;
opt.layer_defs = layer_defs;
opt.tdtrainer_options = tdtrainer_options;

brain = new deepqlearn.Brain(num_inputs, num_actions, opt);

// CUSTOM_VARS_BEGIN
var gen_name = 'C1';
var count = 0;
var eval = false;
var save_checkpoint = 500;
var eval_start = 2000;
var target_mph = 69.90;
// CUSTOM_VARS_END

learn = function (state, lastReward) {
    brain.backward(lastReward);
    var action = brain.forward(state);

// CUSTOM_CODE_BEGIN
    function getFixedData() {
        var data = editor.getValue() + "\n/*###########*/\n";
        data = data.replace("otherAgents = 0","otherAgents = 10");
        if (brain) {
            data += "if (brain) {\nbrain.value_net.fromJSON(" + JSON.stringify(brain.value_net.toJSON()) + ");\n}";
        }
        return data;
    }

    downloadNamedCode = function (thisName, forward_passes, data) {
        var blob = new Blob([data], {type: 'text/plain'});
        var url = URL.createObjectURL(blob);
        var blobAnchor = document.getElementById("blobDownload");
        blobAnchor.download = "net-" + gen_name + '-' + forward_passes + '-' + thisName + ".js";
        blobAnchor.href = url;
        blobAnchor.click();
    }

    if (typeof(count) != "undefined") {
        if(brain.forward_passes >= eval_start) {
            if(brain.learning == false) {
                count = count + 1
                if(count >= save_checkpoint) {
                    if(brain.forward_passes > 0){
                        if(eval === false && self.document !== undefined) {
                            thisData = getFixedData();
                            var myWorker = new Worker("eval_webworker.js");
                            eval = true;
                            myWorker.onmessage = function (e) {
                                if (typeof e.data.percent != 'undefined') {
                                    // do nothing / placeholder
                                }
                                if (typeof e.data.mph != 'undefined') {
                                    console.log('Eval complete - ' + e.data.mph);
                                    if(e.data.mph >= target_mph) {
                                        console.log('Saving checkpoint at ' + brain.forward_passes);
                                        downloadNamedCode(e.data.mph, brain.forward_passes, thisData);
                                    }
                                    eval = false;
                                }
                            };
                            myWorker.postMessage(getData());
                        }
                    }
                    count = 0;
                }
            }
        }
    }
// CUSTOM_CODE_END

    draw_net();
    draw_stats();
    return action;
}

//]]>