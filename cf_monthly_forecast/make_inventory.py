# create an inventory file for a specific directory

from glob import glob
import os
from datetime import datetime
from cf_monthly_forecast.config import dirs
import re


def main(inv_directory,pattern='*'):
    """
    
    """
    search_pattern = os.path.join(inv_directory,pattern)
    inventory = glob(search_pattern)

    # get file size and sort list from largest to smallest files:
    inventory_ext = sorted([(el,os.stat(el).st_size) for el in inventory],key=lambda x: x[1],reverse=True)
    empty_files = [inv_el[0] for inv_el in inventory_ext if inv_el[1] == 0]

    inventory_flagged = ['0MB\t*{file:s}'.format(file=inv_el[0]) if inv_el[1]==0 else '{size:0.1f}MB\t{file:s}'.format(size=inv_el[1]/(1024**2),file=inv_el[0]) for inv_el in inventory_ext]

    today = datetime.today()

    invfile = 'inventory_{3:s}-{0:0>4d}_{1:0>2d}_{2:0>2d}_0.txt'.format(today.year,today.month,today.day,search_pattern.split('/')[-2])
    inv_name = os.path.join(dirs['inventory'],invfile)
    while os.path.exists(inv_name):
        current_num = int(re.search('_(\d+).txt',inv_name).groups()[0])
        new_num = current_num + 1
        inv_name = inv_name.replace('_{0:d}.txt'.format(current_num),'_{0:d}.txt'.format(new_num))
        # note that this will lead to creation of files like ..._1_1.txt and so on

    # insert a header for the file:
    HEADER = 'Inventory of directory {dir:s} on {date:}. Contains {n_empt:d} empty files (flagged with *).'.format(dir=inv_directory,date=today,n_empt=len(empty_files))
    inventory_flagged.insert(0,HEADER)
    # transform the inventory list to a string:
    inv_inp = '\n'.join(inventory_flagged)
    
    # save to file
    with open(inv_name,'w') as infl:
        infl.write(inv_inp)


if __name__ == '__main__':
    direct = input('Which directory should the inventory be made for? ')
    if os.path.exists(direct):
        main(direct)
    else:
        print('Specified directory does not exist!')