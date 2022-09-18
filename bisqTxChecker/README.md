### bisqTxChecker

This is a tool developed to check onchain data of bisq trades, looking for ones which never paid out.
See https://github.com/bisq-network/proposals/issues/352 for background on why this is useful.

In addition to finding locked multisigs, it attempts to gather some statistics:

- number of trades analyzed
- canceled or failed trades that paid the fee in BSQ
- canceled or failed trades that paid the fee in BTC
- locked multisigs that had the fee paid in BSQ
- locked multisigs that had the fee paid in BTC


For simplicity's sake, it does not report trades prior to 2020, since there were a lot of different fee receiving addresses and the protocol was different (2 of 3 multisig).

It does not check very recent trades, as they may still be pending for a couple of months.


### Install & run

Requirements: bitcoin full node; Fulcrum or other Electrum server on localhost; python 3.8.


    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python3 bisqTxChecker.py


This will process the txn data files in the local directory, and eventually produce a file [report.txt](report.txt)
  
e.g.

    [transaction details with date and amount locked]
    deposit=dda9eb04c7ed6a05ec33b131d34f06866c47b45cd923e4269019bc430d450fab feePayment=71a7f0d2a5be250e774d8a80ccdeb387f3afd9c15649b559de8c17bbf8281f59 date=2020-08-24 value=2.84390214
    deposit=dda9eb04c7ed6a05ec33b131d34f06866c47b45cd923e4269019bc430d450fab feePayment=8805b5f3ad1ba191cb06d9c643df51b009a63df3828ca7e6167961d626370230 date=2020-08-24 value=2.84390214
    
    268359 fee payment txs analyzed
    134179 trades analyzed
    58 trades with locked/abandoned multisig
    10006 of 102595 BSQ fee payments resulting in cancel offer or failed trade
    14341 of 165764 BTC fee payments resulting in cancel offer or failed trade
    33 of 102595 BSQ fee payments resulting in locked multisig
    73 of 165764 BTC fee payments resulting in locked multisig
    5.94173536 BTC total locked value
    
    
### Tx Source Data

This utility does some checking based on lists of Bisq trade fee txs.
The lists are included for ease of use (filenames `bisqTradeTxns_*.txt`).

Alternatively the utility can boostrap its own data set, see the commented out code in `main`.

Bootstrapping involves calling a mempool.space API to lookup transactions from Bisq fee addresses.

BSQ fee transactions are sourced from the Bisq application itself, using this patch: [bsqPatch.patch](bsqPatch.patch) and stored in the file `bisqTradeTxns_bsq.txt`


