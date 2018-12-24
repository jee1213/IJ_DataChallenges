import csv
from collections import defaultdict,Counter
import os
# depending on which year data you are looking at, we need to download files from the department of labor web page.
# since there is no good standardized naming convention for the flies, the 'name' module creates url and filename
# for each year the user inputs.   
def name(yearstr):
	year = int(yearstr)
	if 2007< year <= 2011:
		url = 'https://www.foreignlaborcert.doleta.gov/docs/lca/'
		if year < 2010:
			filename = 'H-1B_Case_Data_FY%d'%(year)
		elif year == 2010:
			filename = 'H-1B_FY2010'
		else:
			filename = 'H-1B_iCert_LCA_FY2011_Q4'
	elif year == 2012:
		url = 'https://www.foreignlaborcert.doleta.gov/docs/py2012_q4/'
		filename = 'LCA_FY2012_Q4'
	elif year == 2013:
		url = 'https://www.foreignlaborcert.doleta.gov/docs/lca/'
		filename = 'LCA_FY2013'
	elif (year > 2013) and (year <2016):
		url = 'https://www.foreignlaborcert.doleta.gov/docs/py%dq4/'%(year)
		if year == 2014:
			filename = 'H-1B_FY14_Q4'
		else:
			filename = 'H-1B_Disclosure_Data_FY15_Q4'
	elif year == 2016:
		url = 'https://www.foreignlaborcert.doleta.gov/docs/Performance_Data/Disclosure/FY15-FY16/'
		filename = 'H-1B_Disclosure_Data_FY16'
	elif year == 2017:
		url = 'https://www.foreignlaborcert.doleta.gov/pdf/PerformanceData/2017/'
		filename = 'H-1B_Disclosure_Data_FY17'
	else:
		ValueError
		print('please input a year between 2008-2017')
	print(url,filename)
	return url, filename
# if the xlsx file for the year of interest does not exist, we download the file from the database.
def download(year,inputDir,url,filename):
	os.system('wget %s%s -P ../input/.'%(url,filename+'.xlsx'))
	print('Download complete, converting xlsx to csv')
	os.system('xlsx2csv %s%s %s%s'%(inputDir,filename+'.xlsx',inputDir,filename+'.csv'))
	print('Conversion complete')
inputDir = '../input/'
outputDir = '../output/'
year = input('input year of interest (2008-2017): ')
if year == '':
	print('proceed to the test case')
	filename = 'h1b_input'	
else:
	url, filename = name(year)
# check if the xlsx file exist
try:
	print(os.path.isfile(inputDir+filename+'.xlsx'))
	f = open(inputDir+filename+'.csv', 'r')
	f.close()
# if it does not, download using wget
except:
	print('file does not exist for year %s, downloading...'%year)
	download(year,inputDir,url,filename) 
	pass
columns = defaultdict(list)
print('read file')
with open(inputDir+filename+'.csv') as csvfile:
	if year == '':
		data = csv.DictReader(csvfile,delimiter=';')
	else:
		data = csv.DictReader(csvfile)
	for row in data:
		for (k,v) in row.items():
			columns[k].append(v)
# make keys uniform: depends on year, the name of key varies sightly
soc_name = [k for k in columns if 'SOC_NAME' in k]
status = [k for k in columns if 'STATUS' in k]
emp_state = [k for k in columns if 'WORKSITE_STATE' in k]
print(soc_name,status,emp_state)
# change dictionary keys that varies to standard keys
columns['SOC_NAME'] = columns.pop(soc_name[0]) 
columns['CASE_STATUS'] = columns.pop(status[0]) 
columns['WORKSITE_STATE'] = columns.pop(emp_state[0]) 

# Create the list of dictionaries where it only contains certified cases
certified = defaultdict(list)
for i in range(len(columns['CASE_STATUS'])):
	if columns['CASE_STATUS'][i] == 'CERTIFIED':
		certified['SOC_NAME'].append(columns['SOC_NAME'][i])
		certified['WORKSITE_STATE'].append(columns['WORKSITE_STATE'][i])
total_certified = len(certified['SOC_NAME'])
x_cert = Counter(certified['SOC_NAME'])
y_cert = Counter(certified['WORKSITE_STATE'])
len_SOC = min(10,len(x_cert))
len_STATE = min(10,len(y_cert))
print('# of occupations: ',len_SOC, '# of states: ',len_STATE)
#import operator
# order it first by descending # of certified cases, then second by alphabetical order of (soc_name / state).
list1 = sorted(x_cert.most_common(len_SOC), key=lambda x:(-x[1], x[0]))
list2 = sorted(y_cert.most_common(len_STATE), key=lambda x:(-x[1], x[0]))
#list2 = sorted(y_cert.most_common(len_STATE), key=operator.itemgetter(1, 0))
# save files
print('write file')
with open(outputDir+'top_10_occupations_%s.txt'%(year),'w') as f:
    f.write("TOP_OCCUPATIONS;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE\n")
    for i in range(len_SOC):
        f.write("%s;%d;%.1f%%\n"%(list1[i][0],list1[i][1],100.*list1[i][1]/total_certified))
with open(outputDir+'top_10_states_%s.txt'%(year),'w') as f:
    f.write("TOP_STATES;NUMBER_CERTIFIED_APPLICATIONS;PERCENTAGE\n")
    for i in range(len_STATE):
        f.write("%s;%d;%.1f%%\n"%(list2[i][0],list2[i][1],100.*list2[i][1]/total_certified))
