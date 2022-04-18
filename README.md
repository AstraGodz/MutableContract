# MutableContract

A wrapper around [Slither](https://github.com/crytic/slither) to insert pieces of code at specific places in a contract. When testing a smart contract with [Echidna](https://github.com/crytic/echidna) I had to open a contract and insert variables and tests manually, however sometimes I know what I want to test for a bunch of contracts so it would be much easier to just insert test code with Python :)
