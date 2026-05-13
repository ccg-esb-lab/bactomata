

###################################################################################
#
# SCRIPT GENERATED ON 13/05/2026 FROM THE FOLLOWING LAYOUT FILES:
#  fileDictName=experiments/Bactomata_Example/raw/layouts/Bactomata_Example_media_key_dict.txt
#  fileTroughName=experiments/Bactomata_Example/raw/layouts/Bactomata_Example_trough_layout.txt
#  fileLayoutName=experiments/Bactomata_Example/raw/layouts/Bactomata_Example_media_layout.txt
#
###################################################################################
from opentrons import Robot
from opentrons import containers, instruments
from itertools import chain

robot = Robot()

p200rack = containers.load('tiprack-200ul', 'A1', 'tiprack')
trough = containers.load('tube-rack-15_50ml','A2','trough')
for tube in trough:
	tube.properties['height']+=50
plate1 = containers.load('96-PCR-flat','D1','plate-1')
p200 = instruments.Pipette(name='p200',trash_container=trash,tip_racks=[p200rack],min_volume=1,axis='b',channels=1)

p200.set_max_volume(200)

#p200.pick_up_tip(p200rack['0'])
p200.move_to(plate1[0].bottom(), 'arc')
p200.move_to(plate1[95].bottom(), 'arc')

# *********** Dispense AMP

p200.aspirate(200, trough['A3'].bottom(80))
p200.dispense(100, plate1[9].top(-2)).touch_tip() #1 <Slot D1><Well B2>
p200.dispense(100, plate1[17].top(-2)).touch_tip() #2: <Slot D1><Well B3>

p200.aspirate(200, trough['A3'].bottom(80))
p200.dispense(100, plate1[25].top(-2)).touch_tip() #3: <Slot D1><Well B4>
p200.dispense(100, plate1[33].top(-2)).touch_tip() #4: <Slot D1><Well B5>

p200.aspirate(200, trough['A3'].bottom(80))
p200.dispense(100, plate1[41].top(-2)).touch_tip() #5: <Slot D1><Well B6>
p200.dispense(100, plate1[49].top(-2)).touch_tip() #6: <Slot D1><Well B7>

p200.aspirate(200, trough['A3'].bottom(79))
p200.dispense(100, plate1[57].top(-2)).touch_tip() #7: <Slot D1><Well B8>
p200.dispense(100, plate1[65].top(-2)).touch_tip() #8: <Slot D1><Well B9>

p200.aspirate(200, trough['A3'].bottom(79))
p200.dispense(100, plate1[73].top(-2)).touch_tip() #9: <Slot D1><Well B10>
p200.dispense(100, plate1[81].top(-2)).touch_tip() #10: <Slot D1><Well B11>

p200.aspirate(200, trough['A3'].bottom(79))
p200.dispense(100, plate1[11].top(-2)).touch_tip() #11: <Slot D1><Well D2>
p200.dispense(100, plate1[19].top(-2)).touch_tip() #12: <Slot D1><Well D3>

p200.aspirate(200, trough['A3'].bottom(78))
p200.dispense(100, plate1[27].top(-2)).touch_tip() #13: <Slot D1><Well D4>
p200.dispense(100, plate1[35].top(-2)).touch_tip() #14: <Slot D1><Well D5>

p200.aspirate(200, trough['A3'].bottom(78))
p200.dispense(100, plate1[43].top(-2)).touch_tip() #15: <Slot D1><Well D6>
p200.dispense(100, plate1[51].top(-2)).touch_tip() #16: <Slot D1><Well D7>

p200.aspirate(200, trough['A3'].bottom(78))
p200.dispense(100, plate1[59].top(-2)).touch_tip() #17: <Slot D1><Well D8>
p200.dispense(100, plate1[67].top(-2)).touch_tip() #18: <Slot D1><Well D9>

p200.aspirate(200, trough['A3'].bottom(77))
p200.dispense(100, plate1[75].top(-2)).touch_tip() #19: <Slot D1><Well D10>
p200.dispense(100, plate1[83].top(-2)).touch_tip() #20: <Slot D1><Well D11>

p200.aspirate(200, trough['A3'].bottom(77))
p200.dispense(100, plate1[13].top(-2)).touch_tip() #21: <Slot D1><Well F2>
p200.dispense(100, plate1[21].top(-2)).touch_tip() #22: <Slot D1><Well F3>

p200.aspirate(200, trough['A3'].bottom(76))
p200.dispense(100, plate1[29].top(-2)).touch_tip() #23: <Slot D1><Well F4>
p200.dispense(100, plate1[37].top(-2)).touch_tip() #24: <Slot D1><Well F5>

p200.aspirate(200, trough['A3'].bottom(76))
p200.dispense(100, plate1[45].top(-2)).touch_tip() #25: <Slot D1><Well F6>
p200.dispense(100, plate1[53].top(-2)).touch_tip() #26: <Slot D1><Well F7>

p200.aspirate(200, trough['A3'].bottom(76))
p200.dispense(100, plate1[61].top(-2)).touch_tip() #27: <Slot D1><Well F8>
p200.dispense(100, plate1[69].top(-2)).touch_tip() #28: <Slot D1><Well F9>

p200.aspirate(200, trough['A3'].bottom(75))
p200.dispense(100, plate1[77].top(-2)).touch_tip() #29: <Slot D1><Well F10>
p200.dispense(100, plate1[85].top(-2)).touch_tip() #30: <Slot D1><Well F11>

p200.aspirate(200, trough['A3'].bottom(75))
p200.dispense(100, plate1[15].top(-2)).touch_tip() #31: <Slot D1><Well H2>
p200.dispense(100, plate1[23].top(-2)).touch_tip() #32: <Slot D1><Well H3>

p200.aspirate(200, trough['A3'].bottom(75))
p200.dispense(100, plate1[31].top(-2)).touch_tip() #33: <Slot D1><Well H4>
p200.dispense(100, plate1[39].top(-2)).touch_tip() #34: <Slot D1><Well H5>

p200.aspirate(200, trough['A3'].bottom(74))
p200.dispense(100, plate1[47].top(-2)).touch_tip() #35: <Slot D1><Well H6>
p200.dispense(100, plate1[55].top(-2)).touch_tip() #36: <Slot D1><Well H7>

p200.aspirate(200, trough['A3'].bottom(74))
p200.dispense(100, plate1[63].top(-2)).touch_tip() #37: <Slot D1><Well H8>
p200.dispense(100, plate1[71].top(-2)).touch_tip() #38: <Slot D1><Well H9>

p200.aspirate(200, trough['A3'].bottom(74))
p200.dispense(100, plate1[79].top(-2)).touch_tip() #39: <Slot D1><Well H10>
p200.dispense(100, plate1[87].top(-2)).touch_tip() #40: <Slot D1><Well H11>

#p200.drop_tip()
#p200.pick_up_tip(p200rack['1'])

# *********** Dispense CHL

p200.aspirate(200, trough['A4'].bottom(80))
p200.dispense(100, plate1[8].top(-2)).touch_tip() #41 <Slot D1><Well A2>
p200.dispense(100, plate1[16].top(-2)).touch_tip() #42: <Slot D1><Well A3>

p200.aspirate(200, trough['A4'].bottom(80))
p200.dispense(100, plate1[24].top(-2)).touch_tip() #43: <Slot D1><Well A4>
p200.dispense(100, plate1[32].top(-2)).touch_tip() #44: <Slot D1><Well A5>

p200.aspirate(200, trough['A4'].bottom(80))
p200.dispense(100, plate1[40].top(-2)).touch_tip() #45: <Slot D1><Well A6>
p200.dispense(100, plate1[48].top(-2)).touch_tip() #46: <Slot D1><Well A7>

p200.aspirate(200, trough['A4'].bottom(79))
p200.dispense(100, plate1[56].top(-2)).touch_tip() #47: <Slot D1><Well A8>
p200.dispense(100, plate1[64].top(-2)).touch_tip() #48: <Slot D1><Well A9>

p200.aspirate(200, trough['A4'].bottom(79))
p200.dispense(100, plate1[72].top(-2)).touch_tip() #49: <Slot D1><Well A10>
p200.dispense(100, plate1[80].top(-2)).touch_tip() #50: <Slot D1><Well A11>

p200.aspirate(200, trough['A4'].bottom(79))
p200.dispense(100, plate1[10].top(-2)).touch_tip() #51: <Slot D1><Well C2>
p200.dispense(100, plate1[18].top(-2)).touch_tip() #52: <Slot D1><Well C3>

p200.aspirate(200, trough['A4'].bottom(78))
p200.dispense(100, plate1[26].top(-2)).touch_tip() #53: <Slot D1><Well C4>
p200.dispense(100, plate1[34].top(-2)).touch_tip() #54: <Slot D1><Well C5>

p200.aspirate(200, trough['A4'].bottom(78))
p200.dispense(100, plate1[42].top(-2)).touch_tip() #55: <Slot D1><Well C6>
p200.dispense(100, plate1[50].top(-2)).touch_tip() #56: <Slot D1><Well C7>

p200.aspirate(200, trough['A4'].bottom(78))
p200.dispense(100, plate1[58].top(-2)).touch_tip() #57: <Slot D1><Well C8>
p200.dispense(100, plate1[66].top(-2)).touch_tip() #58: <Slot D1><Well C9>

p200.aspirate(200, trough['A4'].bottom(77))
p200.dispense(100, plate1[74].top(-2)).touch_tip() #59: <Slot D1><Well C10>
p200.dispense(100, plate1[82].top(-2)).touch_tip() #60: <Slot D1><Well C11>

p200.aspirate(200, trough['A4'].bottom(77))
p200.dispense(100, plate1[12].top(-2)).touch_tip() #61: <Slot D1><Well E2>
p200.dispense(100, plate1[20].top(-2)).touch_tip() #62: <Slot D1><Well E3>

p200.aspirate(200, trough['A4'].bottom(76))
p200.dispense(100, plate1[28].top(-2)).touch_tip() #63: <Slot D1><Well E4>
p200.dispense(100, plate1[36].top(-2)).touch_tip() #64: <Slot D1><Well E5>

p200.aspirate(200, trough['A4'].bottom(76))
p200.dispense(100, plate1[44].top(-2)).touch_tip() #65: <Slot D1><Well E6>
p200.dispense(100, plate1[52].top(-2)).touch_tip() #66: <Slot D1><Well E7>

p200.aspirate(200, trough['A4'].bottom(76))
p200.dispense(100, plate1[60].top(-2)).touch_tip() #67: <Slot D1><Well E8>
p200.dispense(100, plate1[68].top(-2)).touch_tip() #68: <Slot D1><Well E9>

p200.aspirate(200, trough['A4'].bottom(75))
p200.dispense(100, plate1[76].top(-2)).touch_tip() #69: <Slot D1><Well E10>
p200.dispense(100, plate1[84].top(-2)).touch_tip() #70: <Slot D1><Well E11>

p200.aspirate(200, trough['A4'].bottom(75))
p200.dispense(100, plate1[14].top(-2)).touch_tip() #71: <Slot D1><Well G2>
p200.dispense(100, plate1[22].top(-2)).touch_tip() #72: <Slot D1><Well G3>

p200.aspirate(200, trough['A4'].bottom(75))
p200.dispense(100, plate1[30].top(-2)).touch_tip() #73: <Slot D1><Well G4>
p200.dispense(100, plate1[38].top(-2)).touch_tip() #74: <Slot D1><Well G5>

p200.aspirate(200, trough['A4'].bottom(74))
p200.dispense(100, plate1[46].top(-2)).touch_tip() #75: <Slot D1><Well G6>
p200.dispense(100, plate1[54].top(-2)).touch_tip() #76: <Slot D1><Well G7>

p200.aspirate(200, trough['A4'].bottom(74))
p200.dispense(100, plate1[62].top(-2)).touch_tip() #77: <Slot D1><Well G8>
p200.dispense(100, plate1[70].top(-2)).touch_tip() #78: <Slot D1><Well G9>

p200.aspirate(200, trough['A4'].bottom(74))
p200.dispense(100, plate1[78].top(-2)).touch_tip() #79: <Slot D1><Well G10>
p200.dispense(100, plate1[86].top(-2)).touch_tip() #80: <Slot D1><Well G11>

#p200.drop_tip()
#p200.pick_up_tip(p200rack['2'])

# *********** Dispense LB

p200.aspirate(200, trough['B3'].bottom(80))
p200.dispense(100, plate1[8].top(-2)).touch_tip() #81 <Slot D1><Well A2>
p200.dispense(100, plate1[16].top(-2)).touch_tip() #82: <Slot D1><Well A3>

p200.aspirate(200, trough['B3'].bottom(80))
p200.dispense(100, plate1[24].top(-2)).touch_tip() #83: <Slot D1><Well A4>
p200.dispense(100, plate1[32].top(-2)).touch_tip() #84: <Slot D1><Well A5>

p200.aspirate(200, trough['B3'].bottom(80))
p200.dispense(100, plate1[40].top(-2)).touch_tip() #85: <Slot D1><Well A6>
p200.dispense(100, plate1[48].top(-2)).touch_tip() #86: <Slot D1><Well A7>

p200.aspirate(200, trough['B3'].bottom(79))
p200.dispense(100, plate1[56].top(-2)).touch_tip() #87: <Slot D1><Well A8>
p200.dispense(100, plate1[64].top(-2)).touch_tip() #88: <Slot D1><Well A9>

p200.aspirate(200, trough['B3'].bottom(79))
p200.dispense(100, plate1[72].top(-2)).touch_tip() #89: <Slot D1><Well A10>
p200.dispense(100, plate1[80].top(-2)).touch_tip() #90: <Slot D1><Well A11>

p200.aspirate(200, trough['B3'].bottom(79))
p200.dispense(100, plate1[9].top(-2)).touch_tip() #91: <Slot D1><Well B2>
p200.dispense(100, plate1[17].top(-2)).touch_tip() #92: <Slot D1><Well B3>

p200.aspirate(200, trough['B3'].bottom(78))
p200.dispense(100, plate1[25].top(-2)).touch_tip() #93: <Slot D1><Well B4>
p200.dispense(100, plate1[33].top(-2)).touch_tip() #94: <Slot D1><Well B5>

p200.aspirate(200, trough['B3'].bottom(78))
p200.dispense(100, plate1[41].top(-2)).touch_tip() #95: <Slot D1><Well B6>
p200.dispense(100, plate1[49].top(-2)).touch_tip() #96: <Slot D1><Well B7>

p200.aspirate(200, trough['B3'].bottom(78))
p200.dispense(100, plate1[57].top(-2)).touch_tip() #97: <Slot D1><Well B8>
p200.dispense(100, plate1[65].top(-2)).touch_tip() #98: <Slot D1><Well B9>

p200.aspirate(200, trough['B3'].bottom(77))
p200.dispense(100, plate1[73].top(-2)).touch_tip() #99: <Slot D1><Well B10>
p200.dispense(100, plate1[81].top(-2)).touch_tip() #100: <Slot D1><Well B11>

p200.aspirate(200, trough['B3'].bottom(77))
p200.dispense(100, plate1[10].top(-2)).touch_tip() #101: <Slot D1><Well C2>
p200.dispense(100, plate1[18].top(-2)).touch_tip() #102: <Slot D1><Well C3>

p200.aspirate(200, trough['B3'].bottom(76))
p200.dispense(100, plate1[26].top(-2)).touch_tip() #103: <Slot D1><Well C4>
p200.dispense(100, plate1[34].top(-2)).touch_tip() #104: <Slot D1><Well C5>

p200.aspirate(200, trough['B3'].bottom(76))
p200.dispense(100, plate1[42].top(-2)).touch_tip() #105: <Slot D1><Well C6>
p200.dispense(100, plate1[50].top(-2)).touch_tip() #106: <Slot D1><Well C7>

p200.aspirate(200, trough['B3'].bottom(76))
p200.dispense(100, plate1[58].top(-2)).touch_tip() #107: <Slot D1><Well C8>
p200.dispense(100, plate1[66].top(-2)).touch_tip() #108: <Slot D1><Well C9>

p200.aspirate(200, trough['B3'].bottom(75))
p200.dispense(100, plate1[74].top(-2)).touch_tip() #109: <Slot D1><Well C10>
p200.dispense(100, plate1[82].top(-2)).touch_tip() #110: <Slot D1><Well C11>

p200.aspirate(200, trough['B3'].bottom(75))
p200.dispense(100, plate1[11].top(-2)).touch_tip() #111: <Slot D1><Well D2>
p200.dispense(100, plate1[19].top(-2)).touch_tip() #112: <Slot D1><Well D3>

p200.aspirate(200, trough['B3'].bottom(75))
p200.dispense(100, plate1[27].top(-2)).touch_tip() #113: <Slot D1><Well D4>
p200.dispense(100, plate1[35].top(-2)).touch_tip() #114: <Slot D1><Well D5>

p200.aspirate(200, trough['B3'].bottom(74))
p200.dispense(100, plate1[43].top(-2)).touch_tip() #115: <Slot D1><Well D6>
p200.dispense(100, plate1[51].top(-2)).touch_tip() #116: <Slot D1><Well D7>

p200.aspirate(200, trough['B3'].bottom(74))
p200.dispense(100, plate1[59].top(-2)).touch_tip() #117: <Slot D1><Well D8>
p200.dispense(100, plate1[67].top(-2)).touch_tip() #118: <Slot D1><Well D9>

p200.aspirate(200, trough['B3'].bottom(74))
p200.dispense(100, plate1[75].top(-2)).touch_tip() #119: <Slot D1><Well D10>
p200.dispense(100, plate1[83].top(-2)).touch_tip() #120: <Slot D1><Well D11>

p200.aspirate(200, trough['B3'].bottom(73))
p200.dispense(100, plate1[12].top(-2)).touch_tip() #121: <Slot D1><Well E2>
p200.dispense(100, plate1[20].top(-2)).touch_tip() #122: <Slot D1><Well E3>

p200.aspirate(200, trough['B3'].bottom(73))
p200.dispense(100, plate1[28].top(-2)).touch_tip() #123: <Slot D1><Well E4>
p200.dispense(100, plate1[36].top(-2)).touch_tip() #124: <Slot D1><Well E5>

p200.aspirate(200, trough['B3'].bottom(73))
p200.dispense(100, plate1[44].top(-2)).touch_tip() #125: <Slot D1><Well E6>
p200.dispense(100, plate1[52].top(-2)).touch_tip() #126: <Slot D1><Well E7>

p200.aspirate(200, trough['B3'].bottom(72))
p200.dispense(100, plate1[60].top(-2)).touch_tip() #127: <Slot D1><Well E8>
p200.dispense(100, plate1[68].top(-2)).touch_tip() #128: <Slot D1><Well E9>

p200.aspirate(200, trough['B3'].bottom(72))
p200.dispense(100, plate1[76].top(-2)).touch_tip() #129: <Slot D1><Well E10>
p200.dispense(100, plate1[84].top(-2)).touch_tip() #130: <Slot D1><Well E11>

p200.aspirate(200, trough['B3'].bottom(71))
p200.dispense(100, plate1[13].top(-2)).touch_tip() #131: <Slot D1><Well F2>
p200.dispense(100, plate1[21].top(-2)).touch_tip() #132: <Slot D1><Well F3>

p200.aspirate(200, trough['B3'].bottom(71))
p200.dispense(100, plate1[29].top(-2)).touch_tip() #133: <Slot D1><Well F4>
p200.dispense(100, plate1[37].top(-2)).touch_tip() #134: <Slot D1><Well F5>

p200.aspirate(200, trough['B3'].bottom(71))
p200.dispense(100, plate1[45].top(-2)).touch_tip() #135: <Slot D1><Well F6>
p200.dispense(100, plate1[53].top(-2)).touch_tip() #136: <Slot D1><Well F7>

p200.aspirate(200, trough['B3'].bottom(70))
p200.dispense(100, plate1[61].top(-2)).touch_tip() #137: <Slot D1><Well F8>
p200.dispense(100, plate1[69].top(-2)).touch_tip() #138: <Slot D1><Well F9>

p200.aspirate(200, trough['B3'].bottom(70))
p200.dispense(100, plate1[77].top(-2)).touch_tip() #139: <Slot D1><Well F10>
p200.dispense(100, plate1[85].top(-2)).touch_tip() #140: <Slot D1><Well F11>

p200.aspirate(200, trough['B3'].bottom(70))
p200.dispense(100, plate1[14].top(-2)).touch_tip() #141: <Slot D1><Well G2>
p200.dispense(100, plate1[22].top(-2)).touch_tip() #142: <Slot D1><Well G3>

p200.aspirate(200, trough['B3'].bottom(69))
p200.dispense(100, plate1[30].top(-2)).touch_tip() #143: <Slot D1><Well G4>
p200.dispense(100, plate1[38].top(-2)).touch_tip() #144: <Slot D1><Well G5>

p200.aspirate(200, trough['B3'].bottom(69))
p200.dispense(100, plate1[46].top(-2)).touch_tip() #145: <Slot D1><Well G6>
p200.dispense(100, plate1[54].top(-2)).touch_tip() #146: <Slot D1><Well G7>

p200.aspirate(200, trough['B3'].bottom(69))
p200.dispense(100, plate1[62].top(-2)).touch_tip() #147: <Slot D1><Well G8>
p200.dispense(100, plate1[70].top(-2)).touch_tip() #148: <Slot D1><Well G9>

p200.aspirate(200, trough['B3'].bottom(68))
p200.dispense(100, plate1[78].top(-2)).touch_tip() #149: <Slot D1><Well G10>
p200.dispense(100, plate1[86].top(-2)).touch_tip() #150: <Slot D1><Well G11>

p200.aspirate(200, trough['B3'].bottom(68))
p200.dispense(100, plate1[15].top(-2)).touch_tip() #151: <Slot D1><Well H2>
p200.dispense(100, plate1[23].top(-2)).touch_tip() #152: <Slot D1><Well H3>

p200.aspirate(200, trough['B3'].bottom(68))
p200.dispense(100, plate1[31].top(-2)).touch_tip() #153: <Slot D1><Well H4>
p200.dispense(100, plate1[39].top(-2)).touch_tip() #154: <Slot D1><Well H5>

p200.aspirate(200, trough['B3'].bottom(67))
p200.dispense(100, plate1[47].top(-2)).touch_tip() #155: <Slot D1><Well H6>
p200.dispense(100, plate1[55].top(-2)).touch_tip() #156: <Slot D1><Well H7>

p200.aspirate(200, trough['B3'].bottom(67))
p200.dispense(100, plate1[63].top(-2)).touch_tip() #157: <Slot D1><Well H8>
p200.dispense(100, plate1[71].top(-2)).touch_tip() #158: <Slot D1><Well H9>

p200.aspirate(200, trough['B3'].bottom(66))
p200.dispense(100, plate1[79].top(-2)).touch_tip() #159: <Slot D1><Well H10>
p200.dispense(100, plate1[87].top(-2)).touch_tip() #160: <Slot D1><Well H11>

p200.aspirate(200, trough['B3'].bottom(66))
p200.dispense(200, plate1[0].top(-2)).touch_tip() #161: <Slot D1><Well A1>

p200.aspirate(200, trough['B3'].bottom(66))
p200.dispense(200, plate1[88].top(-2)).touch_tip() #162: <Slot D1><Well A12>

p200.aspirate(200, trough['B3'].bottom(65))
p200.dispense(200, plate1[1].top(-2)).touch_tip() #163: <Slot D1><Well B1>

p200.aspirate(200, trough['B3'].bottom(65))
p200.dispense(200, plate1[89].top(-2)).touch_tip() #164: <Slot D1><Well B12>

p200.aspirate(200, trough['B3'].bottom(64))
p200.dispense(200, plate1[2].top(-2)).touch_tip() #165: <Slot D1><Well C1>

p200.aspirate(200, trough['B3'].bottom(64))
p200.dispense(200, plate1[90].top(-2)).touch_tip() #166: <Slot D1><Well C12>

p200.aspirate(200, trough['B3'].bottom(64))
p200.dispense(200, plate1[3].top(-2)).touch_tip() #167: <Slot D1><Well D1>

p200.aspirate(200, trough['B3'].bottom(63))
p200.dispense(200, plate1[91].top(-2)).touch_tip() #168: <Slot D1><Well D12>

p200.aspirate(200, trough['B3'].bottom(63))
p200.dispense(200, plate1[4].top(-2)).touch_tip() #169: <Slot D1><Well E1>

p200.aspirate(200, trough['B3'].bottom(63))
p200.dispense(200, plate1[92].top(-2)).touch_tip() #170: <Slot D1><Well E12>

p200.aspirate(200, trough['B3'].bottom(62))
p200.dispense(200, plate1[5].top(-2)).touch_tip() #171: <Slot D1><Well F1>

p200.aspirate(200, trough['B3'].bottom(62))
p200.dispense(200, plate1[93].top(-2)).touch_tip() #172: <Slot D1><Well F12>

p200.aspirate(200, trough['B3'].bottom(62))
p200.dispense(200, plate1[6].top(-2)).touch_tip() #173: <Slot D1><Well G1>

p200.aspirate(200, trough['B3'].bottom(61))
p200.dispense(200, plate1[94].top(-2)).touch_tip() #174: <Slot D1><Well G12>

p200.aspirate(200, trough['B3'].bottom(61))
p200.dispense(200, plate1[7].top(-2)).touch_tip() #175: <Slot D1><Well H1>

p200.aspirate(200, trough['B3'].bottom(61))
p200.dispense(200, plate1[95].top(-2)).touch_tip() #176: <Slot D1><Well H12>
##