from Naked.toolshed.shell import execute_js, muterun_js
import os
from optparse import OptionParser
import time

def run(**kwargs):
	path1 = os.path.join(os.path.abspath('.'),'gsm_simulator','index.js')
	path2 = os.path.join(os.path.abspath('.'),'client','app.js')
	success = execute_js(path1, arguments=kwargs['population']+' &')

	if success:
		success = execute_js(path2)
		if not success:
			print('Unable to run client module')
	else:
		print("Unable to run gsm_simulator module")

if __name__ == '__main__':
	p = OptionParser()
	p.add_option('--population', '-p', dest="population", help="No of persons to be passed to the simulator")
	(options,args) = p.parse_args()
	run(population=options.population)
