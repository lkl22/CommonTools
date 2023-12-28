function process(event) {
    var fp = event.Get("log.file.path");
    var offset = event.Get("log.offset");
    var regExecRes = /(.*)[/\\]+[^/\\]+$/.exec(fp);
    if (regExecRes && regExecRes.length > 1) {
        event.Put("log.file.parentPath", regExecRes[1].trim());
    }
    event.Put("log.file.position", fp + ';' + offset);
    event.Delete("log.file.path");
    event.Delete("log.offset");
    event.Delete("log.file.vol");
    event.Delete("log.file.idxhi");
    event.Delete("log.file.idxlo");
}