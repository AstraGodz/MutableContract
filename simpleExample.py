from MutableContract import MutableContract

mut_contract = MutableContract('original.sol')

mut_contract.insert_code_at(mut_contract.token.Contract.head,
                            b'uint256 public EchidnaVar;',
                            where='within')

mut_contract.insert_code_at(mut_contract.token.Contract.functions.constructor,
                            b'EchidnaVar = 10;',
                            where='within')

mut_contract.insert_code_at(mut_contract.token.Contract.functions.constructor,
                            b'uint256 public pairAdd;',
                            where='before')

mut_contract.insert_code_at(mut_contract.token.Contract.functions._burn,
                            b'require(msg.sender == 0xdac17f958d2ee523a2206206994597c13d831ec7);',
                            where='within')

mut_contract.insert_code_at(mut_contract.token.Contract.tail,
                            '''function echidna_check_balance() public returns(bool) {
        return msg.sender.balance < EchidnaVar;
    }'''.encode('utf-8'),
                            where='within')

mut_contract.dump()
