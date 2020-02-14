*** BIP39 notes ***
Written by github / jmacxx  2020-01-26


Writing this because I found the available online info about BIP39 lacking or hard to understand.
BIP39 is a standard for encoding a cryptographic seed in a phrase of human-readable words.
The cryptographic seed is a large number; it typically represents a master private key (i.e. a key that can
be used to algorithmically derive many sub-keys across different coins).

There are some non-standard variants of BIP39, for example the popular electrum wallet has one which includes a version number in the phrase.

There are two separate use-cases to consider: creating a mnemonic phrase and transforming the mnemonic phrase into a seed (master private key).


Creating a mnemonic phrase
~~~~~~~~~~~~~~~~~~~~~~~~~~
Generate entropy (random number).  Typically 256 bits for a 24 word phrase, although shorter ones are also described in the BIP-39 spec.
Hash the entropy (SHA-256), the checksum will be the first 8 bits of the hash in this example.  Append the checksum bits to the original entropy.
Group the checksummed entropy bits into 11 bit packages.  Each 11 bit number is an index to a word dictionary.  
For 256 bits of entropy (+8 checksum) you would have 264/11=24 words.

Note that the entropy is not the same as the seed which is produced when the mnemonic phrase is decoded.  The hashing is one-way.
    Entropy -> Mnemonic phrase -> seed



Decoding the seed from a mnemonic phrase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When a user inputs the mnemonic phrase, you want to verify that the data is correct by computing the checksum.
Convert the words into 11 bit binary numbers, reverse of above procedure.  Combine into one long binary number.
Split the binary digits into 256 bits (entropy) and 8 bits (checksum)
Hash the entropy bits, the computed checksum will be the first 8 bits of the hash.  Compare this against the 8 bit checksum from above.
If they match, the mnemonic phrase is valid.

A cryptographic function named PBKDF2 is used which takes two strings as input (password and salt) and produces a 64 byte seed as output.
Password is the mnemonic sentence (including a space between each word), salt is hard-coded text "mnemonic" plus a passphrase if one was used.  
PBKDF2 is set to iterate 2048 times using HMAC-SHA512.  Note that any data can be passed in and it will be hashed around to produce a seed output.  
Decoding the seed from mnemonic phrase does not perform any kind of validation on the input.
PBKDF2 is typically provided by a cryptographic library.






Example:
~~~~~~~~
entropy=596f57cad42760e30ca6438862acb090c312d139421ccf73027862ebabe948f2
hash-256 = eb385ac7c289b751aa84bfce5e120ccbc0cb8f4122cb369b5ef26c97ad3a9194, so checksum is eb
Seed word numbers in Binary:

01011001011 => 715 => floor
01111010101 => 981 => kingdom
11110010101 => 1941 => verify
10101000010 => 1346 => portion
01110110000 => 944 => invite
01110001100 => 908 => immense
00110010100 => 404 => crater
11001000011 => 1603 => silent
10001000011 => 1091 => mask
00010101011 => 171 => betray
00101100001 => 353 => club
00100001100 => 268 => canoe
00110001001 => 393 => couple
01101000100 => 836 => hammer
11100101000 => 1832 => topic
01000011100 => 540 => drum
11001111011 => 1659 => sorry
10011000000 => 1216 => object
10011110000 => 1264 => own
11000101110 => 1582 => shift
10111010101 => 1493 => rival
11110100101 => 1957 => visa
00100011110 => 286 => cat
01011101011 => 747 => frost


Python code for generating mnemonic phrase:

	ent = "596f57cad42760e30ca6438862acb090c312d139421ccf73027862ebabe948f2"
	entbytes = codecs.decode(ent, 'hex_codec')
	hd=hashlib.sha256(entbytes).hexdigest()
	ent += hd[0:2]
	entInteger = int(ent, 16)
	entBinary = format(entInteger, '0>264b')
	poslist = []
	for i in range(24):
		binIndex = entBinary[(i*11):((i+1)*11)]
		intIndex = int(binIndex, 2)
		myword = wordlist_english[intIndex]
		print("{:s} => {:d} => {:s}".format(binIndex,intIndex,myword))


Python code for verifying the checksum:

	myWordArray = myMnemonic.split(' ')
	mybigint = sum([wordlist_english.index(w) << (11 * x) for x, w in enumerate(myWordArray[::-1])])
	entHex = format(mybigint, 'x')
	xEntrop = entHex[0:64]
	suppliedChksum = entHex[64:66]
	entbytes = codecs.decode(xEntrop, 'hex_codec')
	hd2=hashlib.sha256(entbytes).hexdigest()
	calcdChecksum = hd2[0:2]
	validChecksum = (calcdChecksum == suppliedChksum)


Python code for converting mnemonic to master private key:

	from hashlib import pbkdf2_hmac
	myMnemonic = 'floor kingdom verify portion invite immense crater silent mask betray club canoe couple hammer topic drum sorry object own shift rival visa cat frost'
	myPassword = '' # optional
	seed = pbkdf2_hmac(hash_name='sha512', password=myMnemonic.encode(), salt=b'mnemonic'+myPassword.encode(), iterations=2048)
	# or (electrum)
    seed = pbkdf2_hmac('sha512',           mnemonic.encode('utf-8'),          b'electrum'+passphrase.encode('utf-8'), iterations = PBKDF2_ROUNDS)

    # 51b3084f27541c35a61fcb7ab9e0e357d0f61f9bc3284f8f95238b95812c9dcfffe0adfaf04990983697bdd00e17a4bff3a921c3a796926e214051a3e437742b




References: 
~~~~~~~~~~

official BIP: 
https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

generating mnemonic phrase & checksum:
https://old.reddit.com/r/Bitcoin/comments/8j56mg

ian coleman BIP39 tool (for decoding mnemonic phrase and deriving keys)
https://github.com/iancoleman/bip39

trezor reference implementation of BIP39 in Python
https://github.com/trezor/python-mnemonic


