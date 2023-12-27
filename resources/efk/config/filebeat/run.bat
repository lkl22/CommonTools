:: 清除es的data stream
curl -X DELETE http://localhost:9200/_data_stream/filebeat-8.11.3

rmdir /s /q data
rmdir /s /q log

filebeat -e -c filebeat.yml
pause