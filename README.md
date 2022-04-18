# MutableContract

_STILL SUPER BETA: have to change a lot still, like more speicifc positions, testing on other contracts, etc. This is just to give an idea_

A wrapper around [Slither](https://github.com/crytic/slither) to insert pieces of code at specific places in a contract. When testing a smart contract with [Echidna](https://github.com/crytic/echidna) I had to open a contract and insert variables and tests manually, however sometimes I know what I want to test for a bunch of contracts so it would be much easier to just insert test code with Python and directly pass it to Echidna without any manual intervention :)

- Can insert new solidity code in and around contract parts, where parts are the header, tail, or functions
- You don't have to think about the order, you can just insert in any order as it will [use `numpy` sorts here](https://github.com/AstraGodz/MutableContract/blob/da9576fc16f407cc5470d2187d374945673259f7/MutableContract.py#L71-L79) to keep track of position shifts
- Dump the output to a new file with the suffix `_inserted`. 

---

Just add a piece of code `before`, `after` or `within` a specified location. 

<b> 1. Create mutable contract object </b>
  
  ```python
  mut_contract = MutableContract('original.sol')
  ```

#### 1. Add state vars

For example to insert code inside the "head" of the contract, i.e. where state variables are defined

```python


mut_contract.insert_code_at(mut_contract.token.Contract.head,
                            b'uint256 public EchidnaVar;',
                            where='within.start')
```
(Note, always have to use `.token` followed by whereever you want to insert)

#### 2. Assign state var in the Constructor
```Python
mut_contract.insert_code_at(mut_contract.token.Contract.functions.constructor,
                            b'EchidnaVar = 10;',
                            where='within.end')
```

#### 3. Add code within a function
I should modify this such that we can say where to insert code within the function, like `function_start` or `function_end`, anyway for now it will just write at the start of the function. So for example to restrict the users calling `_burn` we can do:

```python
mut_contract.insert_code_at(mut_contract.token.Contract.functions._burn,
                            b'require(msg.sender == 0xdac17f958d2ee523a2206206994597c13d831ec7);',
                            where='within')
```

#### 4. Add code before a function
Not sure when you would need this but it's possible :)
```python
mut_contract.insert_code_at(mut_contract.token.Contract.functions.constructor,
                            b'uint256 public pairAdd;',
                            where='before')
```

#### 5. ETC...

#### 6. Write output to the new .sol file
```python
mut_contract.dump()
```

