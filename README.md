# Introduction

Live coding in Python. Our goal is to test for fluency, control, speed and sharpness. We prefer to do this step initially to save time for both you and us in case it's not a good fit. Our exercise takes 50 minutes to complete and involves writing a small micro service using a web framework of your choice (but not Django). Our goal is not to test the knowledge in a specific web framework. If you're not fluent in writing a small web service we suggest you brush up on this.



# Development


```
black .
pylint --disable=R,C,W1203 service.py
```


# Q&A

*   How to change scheduling algorithm?

Method _pick_microservice()  implements round-robin at the moment. It
can implement a different scheme.

*   If you would like to run the load balancer on multiple servers, what is the problem with the current implementation? How would you solve it? 

The dictionary "all_microservices" is local. The dictionary can't be
shared between instances of the load balancer.
There are a few ways to approach the problem.
The easiest is to run a dedicated "register" service. The register
service registers the microservices, updates a shared in-memory
storage (Redis?).  The load balancers proxy the clients requests.  The
load balancers rely on Redis for translation between URL path and (IP
port, IP address) tuple.

In many cases a load balancer can keep the round robin queue locally.
If we need to enforce fairness (robin queue) across all load balancers
we need a dedicated pick_microservice service.


# Links

*  https://stormy-durian-179.notion.site/Info-for-new-candidates-a2615e72706242dc9c77d0c8b1abdc78
*  https://www.youtube.com/watch?v=xB9gF8dUjX4 
