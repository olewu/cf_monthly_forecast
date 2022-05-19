import smtplib
from cf_monthly_forecast.config import email_address 
import re

def send_email(SUBJECT,TEXT,TO=[email_address],FROM = email_address):
    """
    send an email from email address defined in config.py to TO (must be list) with subject SUBJECT and message TEXT, both strings.
    """
    # Prepare actual message
    message = '''From: {0:s}
To: {1:s}
Subject: {2:s}

{3:s}
    '''.format(FROM, ', '.join(TO), SUBJECT, TEXT)

    # Send the mail
    server = smtplib.SMTP('localhost')
    server.sendmail(FROM, TO, message)
    server.quit()


def split_longname_into_varnames(dataset,var_key='variable'):
    """
    split the long_name attribute of a variable with key 'var_key' inside a dataset 'dataset'

    INPUT:
            dataset:    netCDF4._netCDF4.Dataset object as returned when opening netcdf file with Dataset function of the netCDF4 package
            var_names:  list of strings that represent the variable names, e.g. ['2m_temperature','total_precipitation']
    OUTPUT: 
            var_names_sorted:   list of variable names sorted by increasing index in the dataset, e.g. if '2m_temperature' is required from a dataset,
                                the index of '2m_temperature' in the output of this function can be used in the dataarray of the dataset

    """

    var_ix_all = []; var_names_all = []
    repeat = re.compile(r'(?P<start>[0-9]+): (?P<s>\w+)')
    for match in repeat.finditer(dataset.variables[var_key].long_name):
        var_ix_all.append(int(match.groups()[0])); var_names_all.append(match.groups()[1])

    # sort the list of variable names by increasing indices:
    var_names_sorted = [x for _, x in sorted(zip(var_ix_all, var_names_all), key=lambda pair: pair[0])]

    return var_names_sorted

def get_varnums(varlist,var_names):
    """
    get a dictionary that points from each required variable name in 'var_names' to the corresponding index in a list varlist

    INPUT: 
            varlist:    list of strings, each string a variable name, usually output of split_longname_into_varnames(dataset)
            var_names:  list or tuple of strings, each string a requested variable name.
                        If these are expected not to correspond exactly to elements in varlist,
                        define shorthands in the if statements of the function.

    OUTPUT:
            dct:        dictionary pointing from variable to index
    """

    dct = {}
    for key in var_names:
        if key in ['t2']:
            key_t = '2m_temperature'
        elif key in ['pr']:
            key_t = 'total_precipitation'
        elif key in ['wsp']:
            key_t = '10m_wind_speed'
        # ... can define arbitrary number of other shorthands here
        else:
            key_t = key
        
        dct[key] = varlist.index(key_t)
    
    return dct
