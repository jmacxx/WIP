# Segwit notes

*Written by jmacxx  2020-02-18*


I had a very hard time figuring out how to program segwit transactions.  This document is my notes on the subject.

I ACCEPT NO LIABILITY FOR THE ACCURACY OF THIS DOCUMENT, IT IS MY NOTES ONLY FOR MY OWN PERSONAL USE.

### Prerequisite

An understanding of how legacy transactions are built (see 'Bitcoins the Hard Way' #ref:5)


## What is Segwit?

Segwit (Segregated Witness) is a newer Bitcoin transaction format (circa 2017) which separates the signature from the transaction
data.  The reason for this change is to solve the 'transaction malleability problem' in other words a segwit transaction id
will always be the same even if you build and sign the transaction more than once. (#ref:4)

Primarily I'm going to stick to what I think of as 'pure' segwit (e.g. using bech32 addresses);
there is also what I refer to as 'transitional' segwit which is kind of a mashup between the legacy 
and segwit worlds (known as segwit-embedded-in-P2SH).  It was created so existing wallet software would retain some compatibility; I am not going to consider it right now.


## Types of segwit transactions

P2WPKH - Pay To Witness Public Key Hash

P2WSH - Pay To Witness Script Hash

Both P2WPKH and P2WSH use **bech32** for encoding addresses.


### P2WPKH

P2WPKH is the easier of the two.  It is the segwit equivalent of legacy ('1' addresses), i.e. all that 
is needed to spend a UTXO is a private key.    

### P2WSH

P2WSH is the segwit equivalent of legacy ('3' addresses).  The address represents the hash of a [script](https://en.bitcoin.it/wiki/Script).
The only way to spend a P2WSH UTXO is by providing the exact script that will hash to the address, and 
obviously satisfying the script program itself when run on bitcoin core.


### Transaction format

The format of transactions is slightly different than legacy.  
The primary difference is that the transaction hash (aka TxId) is calculated 
by hashing the **data** of the transaction only, whereas in Legacy the TxId is hash of the entire data including signature. (#ref:2)

The witness signature is included in the transaction near the end, just before the locktime field.
Its format is [number of witness fields][length prefixed field][length prefixed field]etc..
The legacy 'scriptSig' field is left empty, i.e. a single '00' byte.
The thing that tells infrastructure if a transaction is segwit or not, is a 'segwit marker' field
which comes directly after the 4 byte transaction version.  The segwit marker is '0001' (2 hex bytes). 
To illustrate it clearly, here is the outline of a legacy compared to a segwit transaction:

    legacy: 01000000      [nIns][prevout][nidx] [scriptSig] [nSequence] [nOuts][amount][addr/script]                      [nLocktime]
    segwit: 01000000 0001 [nIns][prevout][nidx] [00]        [nSequence] [nOuts][amount][addr/script] [nWitness] [witness] [nLocktime]


Witness signature is calculated as follows.  Assemble what is known as the 'hash preimage' from the following available data:

   1. nVersion (4-bytes)
   2. hashPrevouts (32-bytes)           hash of ALL the prevouts
   3. hashSequence (32-bytes)           hash of ALL the nSequence we are using
   4. outpoint (32-bytes + 4-bytes)     the last prevout?
   5. scriptCode (NB. length-prefixed)
   6. in_value of UTXO  (8-bytes)
   7. nSequence of the input (4-bytes)  sequence from outpoint
   8. hashOutputs (32-bytes)
   9. nLocktime of the transaction (usually 0) (4-bytes)
   10. nSighashType (usually 1) (4-bytes)
   (All these fields are fixed length except for the scriptCode).

The preimage is double-SHA256 hashed and the resultant 32 bytes are signed using the private key resulting in the Witness signature.





### TxId

The transaction Id is calculated by double-SHA256 hash of the following unsigned block
Note that there is no segwit marker or witness block here.

    [version][nIns][prevout][nidx][00][nSequence][nOuts][amount][addr/script][nLocktime]





### Funding TX

legacy txn paying to a segwit address

    01000000
    01 
        e42728eca12bebedeae8362b36a38286e51c4c81fa8c0d3342b7ea809283034c 00000000 
        6a 47 304402200dd9bc3aebd32a973e0cd231fdac5c344790de21c5aa0bbb0a447b7e25da84c50220638aae78c0ff36f54f06403be87b409de4132d14c88a84db0facef11297bfde301
           21 03a51cec1cfe9844c9c3e9b536bea8edb22c1fef0af1b55b19dc197170a9e58567
        feffffff
    01 
        401f000000000000 160014a447681601eef322926c0b3de5dfbb4157bbe409
    00000000


Note here that the output address field begins with 00 followed by `[Push20][ripemd160address]`  
The `00` is the indicator that the UTXO is Segwit.  
The `[Push20]` indicates that it is paying to a P2WPKH address.
If it was a `[Push32]` it would be paying to a P2WSH address.




### Redeeming TX (P2WPKH)

In order to spend a segwit UTXO you have to use a segwit transaction:

segwit txn spending a P2WPKH UTXO to a legacy address


    01000000 0001
    01
        71689462853ae52b5e10df0727c82b79e263490fac3388d628f7331f9d067982 00000000
        00
        feffffff
    01
        581b000000000000 1976a914a447681601eef322926c0b3de5dfbb4157bbe40988ac
    02
        48 30450221008daf234f7a33f1ea4623173c28f75ed15ea7233f9f47461f042516d92a201e20022015c87e38a700d2db4914aa86adf1f35ef7b49bb367d766f365369424e381e28601
        21 03a51cec1cfe9844c9c3e9b536bea8edb22c1fef0af1b55b19dc197170a9e58567
    00000000
    (bitcoinjs-lib generated) txId=a8d7e30cf516048d2db5c1ca29f60f7b385df2446403de38f45aebcb76a3d5ce


Here we have a witness that consists of 2 elements: the signature [48 hex bytes long], and the witness script which in this case is a [push_21][public key] because the UTXO type is "witness_v0_keyhash"
The signature must correspond to the hash of the preimage data, signed by the private key.
In other words what bitcoin core does is build the preimage again, and runs a 'signature verification' algorithm. This returns true if the supplied signature was obtained by signing the preimage that matches the public key.



### Redeeming TX (P2WSH)

segwit txn spending a P2WSH UTXO to a legacy address.

This example came from [here](https://bitcoindev.network/guides/bitcoinjs-lib/bitcoin-script-puzzles/).


    01000000 0001
    01
        a6bf33ccfa220b3412d1d06df6daec217ae263c775e6cb18fbd7b3d990b73aa6 00000000
        00
        feffffff
    01
        800c000000000000 1976a914a447681601eef322926c0b3de5dfbb4157bbe40988ac
    03
        01 02
        01 03
        03 935587
    00000000
    txId=b46682d04aefbe774f5d3140ca9186f564c0a6be8124b7941006eb574588b83d

Here we have a witness section consisting of 3 elements: script parameters (02 and 03 pushed on the stack) followed by the script itself (935587).
Translated that means `OP_ADD OP_5 OP_EQUAL`.  Since 02 03 OP_ADD is equal to 5 the script evaluates to true and the UTXO can be spent.
Note that this is a simplistic example and that the script does not require a signature to be spent.
(*Interesting to note that 02 and 03 are pushed, yet the script contains '55' (OP_5) rather than 05.*)

A more typical script would be a multisig or a timelock.













[TODO] If your transaction spends both legacy and segwit UTXOs together, it will also have to be a segwit transaction. [JMC << need to research this more.]










----
References: 

1. official BIP
https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki

2. example of same transaction, but different TxId
https://bitcoin.stackexchange.com/questions/39363/compute-txid-of-bitcoin-transaction?rq=1

3. explanation of TxId calculation for Segwit
https://bitcoin.stackexchange.com/questions/62044/how-to-compute-segwit-txid

4. explanation of how Segwit solves the malleability problem (scriptSig malleability)
https://bitcoincore.org/en/2016/01/26/segwit-benefits/

5. bitcoins the hard way
http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html

6. bitcoin script
https://en.bitcoin.it/wiki/Script
