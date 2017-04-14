## Show the RTI (real time info) expected arrival time of the next bus

![RTI](img/rti.png)
![Item info screenshot](img/info.png)

### Example config:
```
sensor:
  - platform: metlink
    stop_number: 1000
    route_number: 1
  - platform: metlink
    stop_number: 1000
    route_number: 10
  - platform: metlink
    stop_number: 1000
    route_number: 32

```

## Credit

Based on the research of @reedwade https://github.com/reedwade/metlink-api-maybe
