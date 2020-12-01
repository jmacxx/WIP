regtest.
Testing Emergency Broadcast functionality on Bisq

Was using "Alice" and "Bob" to initiate trades that are brought to completion by "Chris" (mediator).
Completed one trade betwenn Alice and Bob using Chris.
Trade completed successfully.
Started a new trade between Alice and Bob.
When Alice took Bob's offer, all hell broke loose and Alice's offer picked up payout made by Chris on previous trade.


**Second instance of the problem happned after clearing all Alice and Bob's Bisq directories, and just trading between the two of them.  The fifth trade picked up the payout TX of the fourth trade.**


### Steps to reproduce:

- Delete user directories for Alice and Bob.
- Start Alice and Bob, wait for them to sync up.
- Fund Alice and Bob's wallets, create payment accounts.
- Bob creates an offer to sell 0.01BTC
- Alice takes the offer
- 1 network confirmation
- Complete the fiat payment to conclude the trade completely and close it.
- Shut down Bisq for Alice and Bob, then restart them both.

- Create a new sell offer made by Bob, taken by Alice
- the problem happens here.  The new trade fails; its deposit transaction is THE SAME AS a payout transaction from one of the previous completed trades.
- sometimes the problem does not happen here, in which case take the trade thru to completion, and repeat.
- the problem seems to randomly occur within 4 trades.

