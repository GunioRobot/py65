import re
from py65.devices.mpu6502 import MPU
from py65.utils.addressing import AddressParser

class Assembler:
    Statement = re.compile(r'^([A-z]{3}\s+'
                           r'\(?\s*)([^,\s\)]+)(\s*[,xXyY\s]*\)?'
                           r'[,xXyY\s]*)$')
                           
    Addressing = [
        ['zpi', re.compile(r'^\(\$00([0-9A-F]{2})\)$')],            # "($0012)"
        ['zpx', re.compile(r'^\$00([0-9A-F]{2}),X$')],              # "$0012,X"
        ['zpy', re.compile(r'^\$00([0-9A-F]{2}),Y$')],              # "$0012,Y"
        ['zpg', re.compile(r'^\$00([0-9A-F]{2})$')],                # "$0012"
        ['inx', re.compile(r'^\(\$00([0-9A-F]{2}),X\)$')],          # "($0012,X)"
        ['iny', re.compile(r'^\(\$00([0-9A-F]{2})\),Y$')],          # "($0012),Y"
        ['ind', re.compile(r'^\(\$([0-9A-F]{2})([0-9A-F]{2})\)$')], # "($1234)"
        ['abx', re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2}),X$')],   # "$1234,X"
        ['aby', re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2}),Y$')],   # "$1234,Y"
        ['abs', re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2})$')],     # "$1234"
        ['rel', re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2})$')],     # "$1234"
        ['imp', re.compile(r'^$')],                                 # ""
        ['acc', re.compile(r'^$')],                                 # ""
        ['acc', re.compile(r'^A$')],                                # "A"
        ['imm', re.compile(r'^#\$([0-9A-F]{2})$')]                  # "#$12"
    ]
    
    def __init__(self, mpu, address_parser=None):
        """ If a configured AddressParser is passed, symbolic addresses
        may be used in the assembly statements.
        """
        if address_parser is None:
            address_parser = AddressParser()

        self._mpu = mpu
        self._address_parser = address_parser

    def assemble(self, statement, pc=0000):
        """ Assemble the given assembly language statement.  If the statement
        uses relative addressing, the program counter (pc) must also be given.
        The result is a list of bytes, or None if the assembly failed.
        """
        opcode, operands = self.normalize_and_split(statement)
        
        for mode, pattern in self.Addressing:
            match = pattern.match(operands)

            if match:
                try:
                    bytes = [ self._mpu.disassemble.index((opcode, mode)) ]
                except ValueError:
                    continue

                operands = match.groups()

                if mode == 'rel':
                    # relative branch
                    absolute = int(''.join(operands), 16)
                    relative = (absolute - pc) - 2
                    relative = relative & 0xFF
                    operands = [ ("%02x" % relative) ]

                elif len(operands) == 2:
                    # swap bytes
                    operands = (operands[1], operands[0])

                operands = [ int(hex, 16) for hex in operands ]
                bytes.extend(operands)
                return bytes

        # assembly failed
        return None
            
    def normalize_and_split(self, statement):
        """ Given an assembly language statement like "lda $c12,x", normalize
            the statement by uppercasing it, removing unnecessary whitespace,
            and parsing the address part using AddressParser.  The result of
            the normalization is a tuple of two strings (opcode, operands).
        """

        # normalize target in operand
        match = self.Statement.match(statement)
        if match:
            before, target, after = match.groups()

            # target is an immediate number
            if target.startswith('#'):
                number = self._address_parser.number(target[1:])
                if (number < 0x00) or (number > 0xFF):
                    raise OverflowError
                statement = '%s#$%02x' % (before, number)

            # target is the accumulator
            elif target in ('a', 'A'): 
                pass

            # target is an address or label
            else:
                address = self._address_parser.number(target)
                statement = '%s$%04x%s' % (before, address, after)
        
        # strip unnecessary whitespace
        opcode  = statement[:3].upper()
        operand = ''.join(statement[3:].split()).upper().strip()
        return (opcode, operand)
