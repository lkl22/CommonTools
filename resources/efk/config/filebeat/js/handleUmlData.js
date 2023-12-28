function process(event) {
    var message = event.Get('message');
    var regExecRes = /(.*)(@startuml.*@enduml)/.exec(message);
    var fields = ['message', 'umlData'];
    if (regExecRes && regExecRes.length > 1) {
        for (var i = 1; i < regExecRes.length; i++) {
            if (i === 2) {
                var umlData = regExecRes[i].trim().replace('&', '\n');
                event.Put(fields[i - 1], umlData);
                event.Put('imageId', event.Get('@metadata._id'));
            } else {
                event.Put(fields[i - 1], regExecRes[i].trim());
            }
        }
    }
}