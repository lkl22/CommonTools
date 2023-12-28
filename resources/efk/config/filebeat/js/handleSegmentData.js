function process(event) {
    var message = event.Get('message');
    message = message.replace('Segment Data[0]', '');
    // 必须完全匹配，不能直接使用.*，否则会替换多余的
    message = message.replace(/\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}\s+\d+[\s-]+\d+[\w/?\.]*\s*\w{1}\s+[^:]+:\s+Segment Data\[\d+\]: /g, '');
    event.Put('message', message);
}