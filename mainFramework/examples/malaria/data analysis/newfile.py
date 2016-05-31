from progressbar import ProgressBar
from time import sleep
pbar = ProgressBar()
my_list = [1,2,3,4,5,6,7,8]
for x in pbar(my_list):
  print 'a'
  sleep(0.1)
pbar = ProgressBar()
my_list=[1,2,3,4,5]
for x in pbar(my_list):
  print 'a'
  sleep(0.1)
