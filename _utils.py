import os 
import re
import glob
import fnmatch
import xmltodict
import json
from IPython.display import HTML, JSON, FileLink
import pandas as pd

def write_json(data, fpth='data.json', sort_keys=True, indent=4):
    '''
    write output to json file
    Args:
        data
        ** sort_keys = True
        ** indent=4
        ** fpth='data.json'
        
    Code:
        out=json.dumps(data, sort_keys=sort_keys, indent=indent)
        f = open(fpth,"w")
        f.write(out)
        f.close()
        return fpth
    '''
    out=json.dumps(data, sort_keys=sort_keys, indent=indent)
    f = open(fpth,"w")
    f.write(out)
    f.close()
    return fpth

def fpth_chg_extension(fpth, new_ext='docx'):
    return os.path.splitext(fpth)[0] + '.' + new_ext

def df_from_list_of_dicts(list_of_dicts,
                          li_of_keys=["@id", "@zoneIdRef", "@conditionType", "@buildingStoreyIdRef", "Name", "Area",
                                      "Volume", "CADObjectId", "TypeCode"]):
    """
    extract listed di items from a list of dicts.
    build list of extracted dicts into dataframe.

    Example:
        list_of_dicts=gbjson["gbXML"]["Campus"]["Building"]["Space"]
        li_of_keys=["@id","@zoneIdRef","@conditionType","@buildingStoreyIdRef","Name","Area","Volume","CADObjectId","TypeCode"]
        df=df_from_list_of_dicts(list_of_dicts,li_of_keys=li_of_keys)
    """
    df = pd.DataFrame(columns=li_of_keys)
    for li_di in list_of_dicts:
        di = {}
        for l in li_of_keys:
            try:
                di[l] = li_di[l]
            except:
                di[l] = 'na'
        df = df.append(di, ignore_index=True)
    return df

def recursive_glob(rootdir='.', pattern='*', recursive=True):
    """ 
    Search recursively for files matching a specified pattern.
    
    name: 
        20180506~3870~code~pyfnctn~jg~recursive_glob~A~0
    tags: 
        rootdir, pattern, finding-files
    Reference: 
        Adapted from: http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
        string pattern matching: https://jakevdp.github.io/WhirlwindTourOfPython/14-strings-and-regular-expressions.html
    Args:
        **rootdir (string): the directory that you would like to recursively search. 
            recursive means it will automatically look in all folders within this directory
        **pattern (string): the filename pattern that you are looking for.
        **recursive (bool): define if you want to search recursively (in sub-folders) or not. 
        
    Returns:
        matches(list): list of filedirectories that match the pattern
    Example:
        rootdir='J:\J'+'J9999'
        pattern='????????_????_?*_?*_?*_?*_?*_?*'
        recursive_glob(rootdir=rootdir, pattern=pattern, recursive=True)
    """
    matches=[]
    if recursive ==True:
        for root, dirnames, filenames in os.walk(rootdir):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))

    else:

        for filename in glob.glob1(rootdir,pattern):
            matches.append(os.path.join(rootdir,filename))
            
    return matches

def write_json(data, fpth='data.json', sort_keys=True, indent=4):
    '''
    write output to json file
    Args:
        data
        ** sort_keys = True
        ** indent=4
        ** fpth='data.json'
        
    Code:
        out=json.dumps(data, sort_keys=sort_keys, indent=indent)
        f = open(fpth,"w")
        f.write(out)
        f.close()

        return fpth
    '''
    out=json.dumps(data, sort_keys=sort_keys, indent=indent)
    f = open(fpth,"w")
    f.write(out)
    f.close()
    return fpth

def xml_to_json(FPTH,display_xml=True,json_to_file=False,open_json_file=False):
    '''
    convert from xml format to json format
    '''
    
    with open(FPTH) as fd:
        json_xml = xmltodict.parse(fd.read())
    if display_xml == True:
        display(FileLink(FPTH))
        display(JSON(json_xml))
    if json_to_file:
        fpth_json = os.path.splitext(FPTH)[0]+'.json'
        write_json(json_xml, fpth=fpth_json, sort_keys=True, indent=4)
    return json_xml

