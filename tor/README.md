Example send/receive using external tor service (but on the same machine).
Using an external tor service on a different machine (e.g. gateway) fails, sender cannot connect to receiver.


    $ ./demoTorReceiver 
    Apr-17 15:34:19.974 [main] WARN  d.Main$TorReceiver: org.berndpruenster.netlayer.tor.ExternalTor@35ef1869 
    Apr-17 15:34:25.834 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service yg347dgewpd5qpx3wzcb6mjndebrbtgg6irhtt6ljtw7zygrzzwppbad.onion has been announced to the Tor network. 
    Apr-17 15:34:25.839 [Thread-2] INFO  d.Main$TorReceiver: Tor hidden service published! 
    Apr-17 15:34:25.839 [Thread-2] INFO  d.Main$TorReceiver: HiddenServiceSocket[addr=yg347dgewpd5qpx3wzcb6mjndebrbtgg6irhtt6ljtw7zygrzzwppbad.onion,port=9999] 
    Apr-17 15:34:26.201 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service yg347dgewpd5qpx3wzcb6mjndebrbtgg6irhtt6ljtw7zygrzzwppbad.onion has been announced to the Tor network. 
    Apr-17 15:34:27.097 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service yg347dgewpd5qpx3wzcb6mjndebrbtgg6irhtt6ljtw7zygrzzwppbad.onion has been announced to the Tor network. 
    Apr-17 15:35:42.350 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion has been announced to the Tor network. 
    Apr-17 15:35:43.051 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion has been announced to the Tor network. 
    Apr-17 15:36:14.384 [Thread-2] INFO  d.Main$TorReceiver: new client connected on localhost 49860 
    Apr-17 15:36:20.386 [Thread-2] INFO  d.Main$TorReceiver: read from peer: hello world! 


    $ ./demoTorSender yg347dgewpd5qpx3wzcb6mjndebrbtgg6irhtt6ljtw7zygrzzwppbad.onion:9999
    Apr-17 15:35:33.361 [main] WARN  demoTorSender.TorConnection: org.berndpruenster.netlayer.tor.ExternalTor@188715b5 
    Apr-17 15:35:33.363 [main] INFO  demoTorSender.TorConnection: /home/user/.local/share/Bisq.old/btc_mainnet/tor/hiddenservice 
    Apr-17 15:35:33.404 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:35:36.405 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:35:37.410 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion has been announced to the Tor network. 
    Apr-17 15:35:37.415 [Thread-2] INFO  demoTorSender.TorConnection: Tor hidden service published! 
    Apr-17 15:35:37.415 [Thread-2] INFO  demoTorSender.TorConnection: HiddenServiceSocket[addr=nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion,port=9991] 
    Apr-17 15:35:37.679 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion has been announced to the Tor network. 
    Apr-17 15:35:37.939 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion has been announced to the Tor network. 
    Apr-17 15:35:39.405 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:35:42.351 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion has been announced to the Tor network. 
    Apr-17 15:35:42.405 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:35:43.051 [TorControlParser] INFO  o.b.netlayer.tor.Tor: Hidden Service nyvb34ypjaiccyizqrctibopjs4tvgntkr2eqmsghk23bwr5vwv2hbad.onion has been announced to the Tor network. 
    Apr-17 15:35:45.406 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:35:48.406 [main] INFO  demoTorSender.Main: connecting to yg347dgewpd5qpx3wzcb6mjndebrbtgg6irhtt6ljtw7zygrzzwppbad.onion:9999 
    Apr-17 15:36:14.888 [main] INFO  demoTorSender.Main: TorSocket[addr=yg347dgewpd5qpx3wzcb6mjndebrbtgg6irhtt6ljtw7zygrzzwppbad.onion,port=9999, localPort=0] 
    Apr-17 15:36:14.888 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:36:17.888 [main] INFO  demoTorSender.Main: writing to socket...hello world!
    Apr-17 15:36:17.888 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:36:20.889 [main] INFO  demoTorSender.Main: waiting... 
    Apr-17 15:36:23.889 [main] INFO  demoTorSender.Main: closed socket 
    Apr-17 15:36:23.889 [main] INFO  demoTorSender.Main: Finished. 


