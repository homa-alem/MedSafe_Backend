import xlrd

from text2num import text2num
import re
#attempt to use specified rules to identify quantities and remove extraneous units
def remUnits(text):
	if(text == ' ' or text.lower() == 'unknown' or text.lower() == 'to be determined'):
		return 'N/A'
	if('million' in text.lower()):
		pieces = text.replace('~', '').replace(',','').split()
		idx = pieces.index('million') - 1
		million_mult = 1000000
		try:
			return int(pieces[idx]) * million_mult
		except ValueError:
			return int(float(pieces[idx]) * million_mult)
	if('=' in text.lower() or 'version' in text.lower() or 'total' in text.lower() or '(' in text.lower() or '/' in text.lower() or ':' in text.lower() or 'of' in text.lower() or 'each' in text.lower() or 'per' in text.lower() or 'in' in text.lower() or '--' in text.lower()):
		temt = text.replace(',', '').replace('-', '').replace('/', ' / ')#text.replace('(', '').replace(')', '').replace('/', ' / ').replace(',', '')
		pieces = temt.split()
		nams = []
		for guess in pieces:
			try:
				frag = int(guess)
				nams.append(frag)
				continue
			except ValueError:
				pass
			try:
				frag = float(guess)
				nams.append(frag)
				continue
			except ValueError:
				continue
		if(nams != []):
			if('=' in text.lower()):
				return nams[len(nams)-1]
			if('version' in text.lower()):
				return nams[0]
			if('/' in text.lower() or 'of' in text.lower() or 'each' in text.lower() or 'per' in text.lower()):
				try:
					return nams[0]*nams[1]
				except IndexError:
					return nams[0]
			elif('total' in text.lower() or '--' in text.lower() or '(' in text.lower()):
				return nams[0]
			elif(':' in text.lower() or 'in' in text.lower()):
				return sum(nams)
	text = re.sub(r'\([^)]*\)', '', text).replace(', ', ',')
	runningString = ''
	bool = True
	lastChar = ''
	for x in list(text):
		if(lastChar == 'Z'):
			if(x == '-'):
				break
		if x.isdigit() or x == ',' or x == '.':
			runningString += x
			bool = True
		else:
			if bool:
				runningString += ' '
				bool = False
		lastChar = x
	#split by spaces
	pieces = runningString.split(' ')
	tot = 0
	#look through each piece
	check = False
	for fragment in pieces:
		#first attempt is if in format of 'US = 500'
		if('=' in fragment):
			try:
				fragment = fragment.split('=')[1]
				grab = int(fragment)
				tot=tot+grab
				check = True
				continue
			except ValueError:
				pass
		if('.' in fragment):
			try:
				tot = tot+float(fragment)
				check = True
				continue
			except ValueError:
				pass
		if(',' in fragment):
			try:
				tot = tot+int(''.join(fragment.split(',')))
				check = True
				continue
			except ValueError:
				pass
		try:
			tot = tot+int(fragment)
			check = True
		except ValueError:
			continue
	if(check == True):
		return tot
	flag = False
	if(tot == 0):
		pieces2 = text.lower()
		pieces2 = pieces2.split(' ')
		for fragment in pieces2:
			try:
				tot = tot+text2num(fragment)
				flag = True
			except ValueError:
				pass
		if(flag and tot == 0):
			return 0
		if(tot != 0):
			return tot
		if(tot == 0):
			return 'N/A'
	return tot

if(__name__ == '__main__'):
	# '''filename = '../../New_Data/2007.xls'
	# dmpfile = '../../New_Data/dumps_remUnits.txt'
	# fils = open(dmpfile, 'wb')
	# workbook = xlrd.open_workbook(filename)
	# worksheet = workbook.sheet_by_index(0)
	# idx = -1
	# recall = -1
	# for i in xrange(worksheet.ncols):
	# 	if('Commerce' in worksheet.cell_value(0, i)):
	# 		idx = i
	# 	if('Number' in worksheet.cell_value(0, i)):
	# 		recall = i
	# for k in range(1, worksheet.nrows):
	# 	#if(worksheet.cell_value(k, recall) == 'Z-0364-2007'):
	# 	fils.write(worksheet.cell_value(k, recall) + ' ')
	# 	fils.write(str(worksheet.cell_value(k, idx)) + '\n')
	# 	fils.write(str(remUnits(worksheet.cell_value(k, idx))) + '\n')
	# fils.close()'''
	print remUnits('694/10-pack boxes')

### KNOWN BAD RECALL #'s to look at ###
#	Z-0427-2007 11.4 million lenses (fixed)
#	Z-0715-2007 1.5 million units (fixed)
#	Z-1042-2007 ~33 million vials (25 strips per vial in the US, ~19 million worldwide. (fixed)
#	Z-1178-2007 6.1 million for Z-1178-1181-2007 recalls (fixed)
#	Z-0819-2007 2.5 million for all products (fixed)

#	Z-0704-2007 91 systems (version 5.1 software) (fixed)

#	Z-0909-2007 709  units + 31 units added = 740 (fixed)

#	Z-0669-2007 528/10 packs (fixed)

#	Z-0621-2007 694/10-pack boxes
#	Z-1021-2007 243/10-pouch cartons


#	Z-0390-2007 (Z-0390-2007 6090751 - 791 devices, 6090752 - 656 devices, 6091151 - 381 devices, 6091152 - 132 devices)
#	Z-0392-2007 (- 346 devices, 6090652 - 395 devices, 6090653 - 315 devices)
#	Z-0523-2007 1347 devices; 1067 domestic and 280 international
#	Z-0344-2007 182,678 units for all US products, 2,943,207 units worldwide
#	Z-0645-2007 306 units: 101- Domestic, 205 - Foreign
#	Z-0701-2007 35 units domestically ( 70 units to OUS)
#	Z-0722-2007 42020HW00 - 1,351 units worldwide; 44037HW00 - 314 units worldwide
#	Z-0747-2007 Cat. #6801322 (1 Reagent Pack box per sales unit): 11,761 units; Cat. #6802450 (5 Reagent Pack boxes per sales unit): 4125 units
#	Z-0765-2007 32,190 units of Catalog No: CX 5825
#	Z-0495-2007 Cat. CX4804 - 3,485 Cutter Tips
#	Z-0807-2007 121 boxes (12/box) Lot I0625120, and 121 boxes (12/box) Lot I0627120-01
#	Z-0939-2007 384 units (#000343) and 12 units (#000443).
#	Z-1093-2007 3,794,990 units in Japan (57,252,581 Worldwide)
#	Z-1165-2007 632 cartons (200 units per carton)
#	Z-1189-2007 2,403 cases (100 bottles per case)
#	Z-1221-2007 240 (120 each model / lot)
#	Z-0129-2008 1,794 distributed - 1176 in US and 618 internationally
#	Z-0053-2008 83 within USA, 580 Foreign-Recalled units only cover devices implanted prior to July 2005
