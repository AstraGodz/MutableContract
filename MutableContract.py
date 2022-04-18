from slither.slither import Slither
from addict import Dict
import numpy as np
import copy


class MutableContract:

    def __init__(self, sol_file, rewrite_to=None):
        # Input solidity file
        self.sol_file = sol_file

        # Rewrite to, could also use fileinput with inplace to directly modify the original
        self.output_file = rewrite_to if rewrite_to else '{}_inserted.sol'.format(sol_file.rstrip('.sol'))
        self.new_code = self._copy_input_code()

        # Will use addict as token object to mimic Slither nesting (see below)
        self.token = Dict()
        self.slither = None

        # Parse solidity file with Slither
        self._parse()

        # Keep track of position shifts after inserts
        # for now just a static arrow with 100r rows, i.e. 100 inserts
        # could dynamically scale later
        self.locs = np.zeros(shape=(100, 2), dtype=np.int64)
        self.filled_till_row = 0

    def _get_start_end(self, ob):
        '''
        Gets the start and end from a Slither object with source mapping
        '''
        start = ob.source_mapping['start']
        end = ob.source_mapping['start'] + ob.source_mapping['length']
        return start, end

    def _copy_input_code(self):
        '''
        Reads input solidity file and makes a copy of the text such that we
        can modify that with inserts
        '''
        with open(self.sol_file, 'rb') as in_file:
            return copy.deepcopy(in_file.read())

    def insert_code_at(self, loc_chain, insert_piece, where='after'):
        '''
        This function will insert a piece of code at a given location, here
        the location chain can be given with keys, such as
        - [contract_name]['functions'][func.name]
        or directly from this object like:
        - self.token.contract_name.functions.func_name
        It then uses the start and end information to place the piece correctly
        todo: make before and after more specific like before_start, after_start, before_end etc.
        '''
        if where == 'after':
            pos = loc_chain['end']
        elif where == 'before':
            pos = loc_chain['start']
        elif where == 'within':
            pos = loc_chain['body_start']
        else:
            print('Option not valid, either "before", "after" or "within"')
            return
        self.insert_code(pos, insert_piece)

    def insert_code(self, position, insert_piece):
        # Add spacing around the code to insert, will be messy with everything concatenated
        insert_piece = b'\n   ' + insert_piece + b'\n'
        # Check if we had shifts before the current position
        index = np.searchsorted(self.locs[:, 0], position)
        # Sum the length of inserted code pieces before the current positions
        # and calculate actual location after shift
        shifted_position = position + np.sum(self.locs[:, 1][:index])
        # Store the current insert in the location tracking array
        self.locs[self.filled_till_row, :] = [position, len(insert_piece)]
        # We might insert before those where we inserted before, hence
        # we have to sort the position array
        self.locs = self.locs[self.locs[:, 0].argsort()]
        # Track where in the 2D array we are with tracking positions, just such
        # that we do not override previous inserts...
        self.filled_till_row += 1
        # Insert piece of code into the source code
        self.new_code = self.new_code[:shifted_position] + insert_piece + self.new_code[shifted_position:]

    def dump(self):
        '''
        Dumps rewritten code to a file
        '''
        with open(self.output_file, 'w') as out:
            out.write(self.new_code.decode('utf-8'))

    def _parse(self):
        '''
        Uses Slither to parse the solidity file and then use source mapping to get the boundaries
        of the contract, functions, and space inbetween
        :return:
        '''
        self.slither = Slither(self.sol_file)
        for contract in self.slither.contracts:
            # Get contract info
            contract_name = contract.name

            # Contract base info
            contract_start, contract_end = self._get_start_end(contract)
            self.token[contract_name]['start'] = contract_start
            self.token[contract_name]['end'] = contract_end

            # Track all starts and ends to get space before and after functions but within the contract
            # see below
            starts, ends = [], []

            # Each has a function that we want to add too
            self.token.contract_name.end = contract_end
            for func in contract.functions:
                if not func.name.startswith('slither'):
                    if func.is_constructor:
                        func.name = 'constructor' # For convenience, nameless in Slither

                    # Location parsing
                    start, end = self._get_start_end(func)
                    self.token[contract_name]['functions'][func.name]['start'] = start
                    self.token[contract_name]['functions'][func.name]['end'] = end

                    # To allow "within" function inserts we have to figure out where the function
                    # definition ends, i.e. the body starts
                    def_end = start + self.new_code[start:start + 200].find(b'{')
                    self.token[contract_name]['functions'][func.name]['body_start'] = def_end + 1

                    # Update function boundaries for the whole contract, needed below for head and tail
                    starts.append(start)
                    ends.append(end)

            # Get header and tail
            # Again first we have to find the end of the contract definition to find the start
            # of the contract head - state var space
            # todo: this is a bit messy, does start and end even make sense? and have to check +1 and -1 here
            contract_def_end = contract_start + self.new_code[contract_start:contract_start + 200].find(b'{')
            self.token[contract_name]['head']['start'] = contract_def_end + 1
            self.token[contract_name]['head']['end'] = min(starts) - 1
            self.token[contract_name]['head']['body_start'] = contract_def_end + 1

            # Same for tail
            self.token[contract_name]['tail']['start'] = max(ends)
            self.token[contract_name]['tail']['end'] = contract_end - 1
            self.token[contract_name]['tail']['body_start'] = max(ends) + 1
