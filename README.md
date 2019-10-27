# Remote Tomcat Access Log Parser

This utility assists in retreiving and parsing Tomcat logs on remote hosts and scraping the logs into a json format.
Provided ssh login information, the utility uses sftp to retrieve access logs for a specific service. Then, relevant
information from the logs is scraped into a json format that can be easily parsed and stored.

## Example
Raw tomcat access log on a remote server:
```
127.0.0.1 - - [18/Dec/2018:13:12:23 -0700] "POST /example/create?param1=example1&param2=example2 HTTP/1.1" 201 101 460 "-" "Java/1.8.0_74"
127.0.0.1 - - [18/Dec/2018:13:12:23 -0700] "GET /example HTTP/1.1" 200 345 211 "-" "Java/1.8.0_74"
```
is retrieved and converted to:
```
[
  {
    "response": "201",
    "datetime": "15/Dec/2016:08:22:41",
    "request": "/example/create?param1=example1&param2=example2",
    "host": "127.0.0.1",
    "method": "POST",
    "responseTime": "460"
  },
  {
    "response": "200",
    "datetime": "15/Dec/2016:08:22:41",
    "request": "/example",
    "host": "127.0.0.1",
    "method": "GET",
    "responseTime": "211"
  }
]
```
