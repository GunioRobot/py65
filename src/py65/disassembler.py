from py65.utils.addressing import AddressParser

class Disassembler:
    def __init__(self, mpu, address_parser=None):
        if address_parser is None:
            address_parser = AddressParser()

        self._mpu = mpu
        self._address_parser = address_parser

    def instruction_at(self, pc):
        """ Disassemble the instruction at PC and return a tuple
        containing (instruction byte count, human readable text)
        """

        instruction = self._mpu.ByteAt(pc)
        disasm, addressing = self._mpu.disassemble[instruction]

        if addressing == 'acc':
            disasm += ' A'
            length = 1

        elif addressing ==  'abs':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' ' + address_or_label
            length = 3

        elif addressing ==  'abx':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' %s,X' % address_or_label
            length = 3

        elif addressing ==  'aby':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' %s,Y' % address_or_label
            length = 3

        elif addressing == 'imm':
            byte = self._mpu.ByteAt(pc + 1)
            disasm += ' #$%02x' % byte
            length = 2

        elif addressing == 'imp':
            length = 1

        elif addressing == 'ind':
            address = self._mpu.WordAt(pc + 1)            
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' (%s)' % address_or_label
            length = 3

        elif addressing == 'iny':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' (%s),Y' % address_or_label
            length = 2

        elif addressing == 'inx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' (%s,X)' % address_or_label
            length = 2

        elif addressing == 'rel':
            opv = self._mpu.ByteAt(pc + 1)
            targ = pc + 2
            if opv & (1<<(8-1)):
                targ -= (opv ^ 0xFF) + 1
            else:
                targ += opv
            targ &= 0xffff

            address_or_label = self._address_parser.label_for(targ, 
                '$%04x' % targ)
            disasm += ' ' + address_or_label
            length = 2

        elif addressing == 'zpi':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '($%02x)' % zp_address)
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'zpg':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing ==  'zpx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' %s,X' % address_or_label
            length = 2

        elif addressing ==  'zpy':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' %s,Y' % address_or_label
            length = 2        

        return (length, disasm)
