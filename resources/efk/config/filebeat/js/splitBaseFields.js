function process(event) {
    let message = event.Get("message")
    let regExecRes = /(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+(\d+)[\s-](\d+)[\s/][?]?\s*(\w){1}\s+([^:]+): (.*)/.exec(message);
    let fields = ['tempTime', 'pid', 'tid', 'level', 'domain', 'message']
    if (regExecRes && regExecRes.length > 1) {
        for (let i = 1; i < regExecRes.length; i++) {
            if (i === 1) {
                event.Put(fields[i - 1], new Date().getFullYear() + '-' + regExecRes[i].trim());
            } else {
                event.Put(fields[i - 1], regExecRes[i].trim());
            }
        }
    }
}

function test() {
    var event = process(new Event({message: '12-27 19:55:37.424 26078-263/? I 06666/ohosStudy_DecisionTree: state FAILED #green'}));
    if (event.Get("tempTime") !== Date().getFullYear() + "-12-27 19:55:37.424") {
        throw "expected split base fields failed.";
    }
}