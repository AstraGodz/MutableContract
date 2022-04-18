# MutableContract

_STILL SUPER BETA: have to change a lot still, like more speicifc positions, testing on other contracts, etc. This is just to give an idea_

A wrapper around [Slither](https://github.com/crytic/slither) to insert pieces of code at specific places in a contract. When testing a smart contract with [Echidna](https://github.com/crytic/echidna) I had to open a contract and insert variables and tests manually, however sometimes I know what I want to test for a bunch of contracts so it would be much easier to just insert test code with Python and directly pass it to Echidna without any manual intervention :)

- Can insert new solidity code in and around contract parts, where parts are the header, tail, or functions
- You don't have to think about the order, you can just insert in any order as it will [use `numpy` sorts here](https://github.com/AstraGodz/MutableContract/blob/da9576fc16f407cc5470d2187d374945673259f7/MutableContract.py#L71-L79) to keep track of position shifts
- Dump the output to a new file with the suffix `_inserted`. 

---

### Object usage examples

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
So for example to restrict the users calling `_burn` we can do:

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

#### 5. Add code before a contract; interface e.g.

```python
mut_contract.insert_code_at(mut_contract.token.Contract,
                            '''interface CoolInterface {
    function magic() external pure returns (uint256);
}
'''.encode('utf-8'),
                            where='before')
```

#### 6. Add a function to a contract.

We can also add a function to a contract by inserting it in the Contract tail, like:

```python
mut_contract.insert_code_at(mut_contract.token.Contract.tail,
                            '''function echidna_check_balance() public returns(bool) {
        return msg.sender.balance < EchidnaVar;
    }'''.encode('utf-8'),
                            where='within')
```

#### 7. Etc.. any insert

#### 8. Write output to the new .sol file

```python
mut_contract.dump()
```

### Combining with Slither

Since the Slither nesting is almost identical it's easy to filter for specific information in Slither and insert based
on that. As a meaningless example, lets say we want to insert `return true;` at the start of every function that has a
modifier. When we find that in the loop below (see `chain =`) we cannot simply
say `mut_contract.token.contract_name.functions.func.name` as half would be an actual variable but the rest
strings (`"functions"`). To fix this we can first
call [reduce](https://docs.python.org/3/library/functools.html#functools.reduce) and use the result to
access `mut_contract.token`, voila :)

```python
from MutableContract import MutableContract
from slither.slither import Slither
from functools import reduce
import operator
from slither.core.declarations.modifier import Modifier

solidity_file = 'original.sol'
mut_contract = MutableContract(solidity_file)
slither = Slither(solidity_file)

for contract in slither.contracts:
    for func in contract.functions:
        for icall in func._internal_calls:
            if isinstance(icall, Modifier):
                print(func.name)
                chain = [contract.name, 'functions', func.name]
                chain = reduce(operator.getitem, chain, mut_contract.token)
                mut_contract.insert_code_at(chain, b'return True;', 'within.start')
                break

mut_contract.dump()

```