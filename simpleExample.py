from MutableContract import MutableContract

mut_contract = MutableContract('original.sol')

# Defining state variable
mut_contract.insert_code_at(mut_contract.token.Contract.head,
                            b'uint256 public EchidnaVar;',
                            where='within.start')

# Assigning the state variable in the constructor
mut_contract.insert_code_at(mut_contract.token.Contract.functions.constructor,
                            b'EchidnaVar = 10;',
                            where='within.end')

# Adding a variable before a function, in this case it will add it to the state vars
# before seems pretty useless between functions..
mut_contract.insert_code_at(mut_contract.token.Contract.functions.constructor,
                            b'uint256 public pairAdd;',
                            where='before')

# Insert at the start of a function, in this case to limit a burn call
mut_contract.insert_code_at(mut_contract.token.Contract.functions._burn,
                            b'require(msg.sender == 0xdAC17F958D2ee523a2206206994597C13D831ec7);',
                            where='within')

# Insert Echidna test code at the end of the contract
mut_contract.insert_code_at(mut_contract.token.Contract.tail,
                            '''function echidna_check_balance() public returns(bool) {
        return msg.sender.balance < EchidnaVar;
    }'''.encode('utf-8'),
                            where='within')

# Insert an interface before the contract, can also be after for example
mut_contract.insert_code_at(mut_contract.token.Contract,
                            '''interface CoolInterface {
    function magic() external pure returns (uint256);
}
'''.encode('utf-8'),
                            where='before')



mut_contract.dump()
