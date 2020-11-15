### Spec for alerts.json

The alerts file is keyed by seednode identifier.
For each seednode there is a list of active alert keynames.
For each active alert there is data on the alerting value, startTimestamp, and sentToKeybase count.

It is best explained by this simple example.  It shows that devinsn3xu has two alerting fields "peakNumConnections" and "daoStateChainHeight".

    {
    "sn3bsq3evq": {}, 
    "wizseed3d3": {}, 
    "rm7b56wbrc": {}, 
    "sn3emzy56u": {}, 
    "devinv3rho": {}, 
    "sn4bsqpc7e": {}, 
    "devinsn2te": {}, 
    "devinsn3xu": {
        "peakNumConnections": {"value": "22", "startTimestamp": 1605460126, "sentToKeybase": 1}, 
        "daoStateChainHeight": {"value": "657060", "startTimestamp": 1605460126, "sentToKeybase": 1}
    }, 
    "sn4emzywye": {}, 
    "wizseed7ab": {}, 
    "5quyxpxhey": {}, 
    "723ljisnyn": {}, 
    "sn2bisqad7": {}, 
    "wizseedscy": {}, 
    "sn5emzyvxu": {}, 
    "s67qglwhkg": {}
    }

