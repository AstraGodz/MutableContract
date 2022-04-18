from slither.slither import Slither
from addict import Dict
import numpy as np
import copy


class MutableContract:

    def __init__(self, sol_file, rewrite_to=None):
        # Input solidity file
        self.sol_file = sol_file

        # Rewrite to, could also use fileinput with inplace to directly modify the original
        self.output_file = rewrite_to if rewrite_to else '{}inserted.sol'.format(sol_file.rstrip('sol'))
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

    def insert_code_at(self, loc_chain, insert_piece, where='within start'):
        '''
        This function will insert a piece of code at a given location, here
        the location chain can be given with keys, such as
        - [contract_name]['functions'][func.name]
        or directly from this object like:
        - self.token.contract_name.functions.func_name
        It then uses the start and end information to place the piece correctly
        '''
        if where == 'after':
            pos = loc_chain['end']
        elif where == 'before':
            pos = loc_chain['start']
        elif where == 'within': # default to start
            pos = loc_chain['body']['start']
        elif where == 'within.start':
            pos = loc_chain['body']['start']
        elif where == 'within.end':
            pos = loc_chain['body']['end']
        else:
            print('Option not valid, either "before", "after" or "within", "within.start", "within.end"')
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
        Dumps rewritten code to a file, we worked in bytes all the time to prevent non-ascii shift, hence
        we have to encode again before writing
        '''
        with open(self.output_file, 'w') as out:
            out.write(self.new_code.decode('utf-8'))

    def _find_boundary(self, position):
        '''
        Helper to find the first {, such that we can insert specifically at the start of functions
        I guess 200 should be sufficient to scan for the closing }, otherwise it's a loooooonggg def
        '''

        new = position + self.new_code[position:position + 200].find(b'{') + 1
        return new

    def _parse(self):
        '''
        Uses Slither to parse the solidity file and then use source mapping to get the boundaries
        of the contract, functions, and space inbetween
        '''
        self.slither = Slither(self.sol_file)
        for contract in self.slither.contracts:

            # We will store all the start and end locations of the functions such that we can
            # later determine the space between the contract and the first function (i.e. where the
            # state vars are) and the "tail", space between last function and end of cotnract
            starts, ends = [], []

            # Get contract info
            contract_name = contract.name

            # Contract base info
            contract_start, contract_end = self._get_start_end(contract)
            self.token[contract_name]['start'] = contract_start
            self.token[contract_name]['end'] = contract_end

            # Each has a function that we want to add too
            for func in contract.functions:
                if not func.name.startswith('slither') and func.contract_declarer == contract:
                    if func.is_constructor:
                        func.name = 'constructor' # For convenience, nameless in Slither

                    # Location parsing
                    start, end = self._get_start_end(func)

                    # Update function boundaries for the whole contract, needed below for head and tail
                    starts.append(start)
                    ends.append(end)

                    # Start here means the start of the function definition, not the body
                    # to solve that we search the first { and add that
                    start_body = self._find_boundary(start)
                    end_body   = end - 1 

                    # Store all
                    self.token[contract_name]['functions'][func.name]['start'] = start
                    self.token[contract_name]['functions'][func.name]['body']['start'] = start_body
                    self.token[contract_name]['functions'][func.name]['body']['end'] = end_body
                    self.token[contract_name]['functions'][func.name]['end'] = end


            # Get header and tail
            # Again first we have to find the end of the contract definition to find the start
            # of the contract head - state var space

            # todo: removed start and end, doesn't seem to make much sense for head and tail?
            self.token[contract_name]['head']['body']['start'] = self._find_boundary(contract_start)
            self.token[contract_name]['head']['body']['end'] = min(starts) - 1

            # Same for tail
            self.token[contract_name]['tail']['body']['start'] = max(ends)
            self.token[contract_name]['tail']['body']['end'] = contract_end - 1
