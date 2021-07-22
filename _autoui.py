# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +

from pydantic import BaseModel, ValidationError, validator
import ipywidgets as widgets
from IPython.display import display
import typing
import pandas as pd
import json
import importlib.util
from typing import Optional, List, Dict, Type, Any
from markdown import markdown

def class_obj_from_type_string(class_type_string: str) -> Type:
    """
    given the str(type(Obj)) of an Obj, this function
    imports it from the relevant lib (using getattr and
    importlib) and returns the Obj. 
    
    makes it easy to define class used as a string in a json
    object and then use this class to re-initite it.
    
    Args:
        class_type_string
    Returns: 
        obj
        
    Example:
        
    """
    
    def find(s, ch):
        return [i for i, ltr in enumerate(s) if ltr == ch]
    cl = class_type_string
    ind = find(cl, "'")
    nm  = cl[ind[0]+1:ind[1]]
    nms =  nm.split('.')
    clss = nms[-1:][0]
    mod = '.'.join(nms[:-1])
    return getattr(importlib.import_module(mod), clss)

class FloatText(BaseModel):
    value: float
    options: None
    data_type: str = 'None'
    widget_type: str = 'None'
        
    @validator('value', always=True)
    def make_float(cls, v):
        if type(v) == int:
            return float(v)
        else:
            return v
        
    @validator('data_type', pre=True, always=True)
    def define_type(cls, v):
        return "<class '__main__.FloatText'>"
    
    @validator('widget_type', pre=True, always=True)
    def get_widget_type(cls, v):
        return "<class 'ipywidgets.widgets.widget_float.FloatText'>"
    
class FloatSlider(BaseModel):
    value: float
    options: None
    min: float
    max: float
    data_type: str = 'None'
    widget_type: str = 'None'
        
    @validator('value', always=True)
    def make_float(cls, v):
        if type(v) == int:
            return float(v)
        else:
            return v
        
        
    @validator('data_type', pre=True, always=True)
    def define_type(cls, v):
        return "<class '__main__.FloatSlider'>"
    
    @validator('widget_type', pre=True, always=True)
    def get_widget_type(cls, v):
        return "<class 'ipywidgets.widgets.widget_float.FloatSlider'>"    

class Dropdown(BaseModel):
    value: typing.Any
    options: list
    data_type: str = 'None'
    widget_type: str = 'None'
        
    @validator('data_type', pre=True, always=True)
    def define_type(cls, v):
        return "<class '__main__.Dropdown'>"
    
    @validator('widget_type', pre=True, always=True)
    def get_widget_type(cls, v):
        return "<class 'ipywidgets.widgets.widget_selection.Dropdown'>"
        
    @validator('value')
    def must_not_be_list(cls, v):
        if type(v) == list:
            raise TypeError('value of dropdown must not be a list')
        return v

class SelectMultiple(BaseModel):
    value: list
    options: list
    data_type: str = 'None'
    widget_type: str = 'None'
        
    @validator('data_type', pre=True, always=True)
    def define_type(cls, v):
        return "<class '__main__.SelectMultiple'>"
    
    @validator('widget_type', pre=True, always=True)
    def get_widget_type(cls, v):
        return "<class 'ipywidgets.widgets.widget_selection.SelectMultiple'>"
        
class Checkbox(BaseModel):
    value: bool
    data_type: str = 'None'
    widget_type: str = 'None'
        
    @validator('value', pre=True, always=True)
    def check_not_float_or_int(cls, v):
        if type(v) == float:
            raise ValueError(f'Checkbox needs a bool value but got float') 
        elif type(v) == int:
            raise ValueError(f'Checkbox needs a bool value but got int') 
        else:
            return v

        
    @validator('data_type', pre=True, always=True)
    def define_type(cls, v):
        return "<class '__main__.Checkbox'>"
    
    @validator('widget_type', pre=True, always=True)
    def get_widget_type(cls, v):
        return "<class 'ipywidgets.widgets.widget_bool.Checkbox'>"
        
class Text(BaseModel):
    value: str
    data_type: str = 'None'
    widget_type: str = 'None'
        
    @validator('value', pre=True, always=True)
    def check_value_type(cls, v):
        t = type(v)
        if type(v) != str:
            raise ValueError(f'Text needs a str value but got {t}') 
        return v
    
    @validator('data_type', pre=True, always=True)
    def define_type(cls, v):
        return "<class '__main__.Text'>"
    
    @validator('widget_type', pre=True, always=True)
    def get_widget_type(cls, v):
        return "<class 'ipywidgets.widgets.widget_string.Text'>"
    
    @validator('value')
    def must_not_be_too_long(cls, v):
        if len(v) > 40:
            raise TypeError('length of string to long')
        return v
    
class Textarea(BaseModel):
    value: str
    data_type: str = 'None'
    widget_type: str = 'None'
        
    @validator('data_type', pre=True, always=True)
    def define_type(cls, v):
        return "<class '__main__.Textarea'>"
    
    @validator('widget_type', pre=True, always=True)
    def get_widget_type(cls, v):
        return "<class 'ipywidgets.widgets.widget_string.Textarea'>"
    
    @validator('value')
    def must_not_be_too_short(cls, v):
        if len(v) < 40:
            raise TypeError('length of string too short')
        return v

class Dataframe(BaseModel):
    value: pd.DataFrame
    
    @validator('value', pre=True, always=True)
    def make_dataframe(cls, v):
        if type(v) != pd.DataFrame:
            tmp = pd.DataFrame.from_dict(v)
        else:
            tmp = v
        return tmp
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            pd.DataFrame: lambda v: v.to_dict(),
        }
        
li_types = [FloatText, FloatSlider, Dropdown, SelectMultiple, Checkbox, Text, Textarea] 
        
def _init_ui_data_obj(di_ui, li_types=li_types):
    """initiate data definition from dict"""
    obj = None
    if 'data_type' in di_ui.keys():
        dtype = di_ui['data_type']
        try:
            obj = class_obj_from_type_string(dtype)(**di_ui)
        except:
            raise ValueError(f'A UI object to match your data was not found: {dtype}') 
        return obj
    # try: except: initiation of datatypes. defaults chosen based on the information provided. 
    for l in li_types:
        try:
            if obj is None:
                obj = l(**di_ui)
            else:
                raise ValueError('Multiple UI objects that match your data have been found. Specify type definition more clearly or pass the data_type in definition.') 
        except:
            pass
    if obj is not None:
        return obj
    else:
        raise ValueError('A UI object to match your data was not found') 
        
def _init_ui_data_objs(li_ui, li_types=li_types):
    return [_init_ui_data_obj(di_ui, li_types) for di_ui in li_ui]        

def _init_widget_from_data_obj(obj_ui):
    """initiate a widget from the data definition"""
    return class_obj_from_type_string(obj_ui.widget_type)(**obj_ui.dict())

def _init_widgets_from_data_objs(li_obj_ui):
    """initiate widgets from data objects"""
    return [_init_widget_from_data_obj(obj_ui) for obj_ui in li_obj_ui]


def _markdown(value='_Markdown_',
              **kwargs):
    """
    a simple template for markdown text input that templates required input
    fields. additional user defined fields can be added as kwargs
    """
    _kwargs = {}
    _kwargs['value'] = markdown(value)  # required field
    _kwargs.update(kwargs)  # user overides
    return widgets.HTML(**_kwargs)


class WidgetRowDescription(BaseModel):
    name: str
    label: str
    
class EditListOfDicts():
    """
    builds user input form from a list of dicts by creating a
    loop of EditDict objects.
    """
    def __init__(self, li, li_widget_types=li_types):
        self.li_in = li
        self.li_types = li_types
        self.li_obj_ui = _init_ui_data_objs(self.li_in, self.li_types)
        self.li_widgets = _init_widgets_from_data_objs(self.li_obj_ui)
        self.li_descriptions = self._init_row_descriptions()
        self.li_rows = self._init_rows()
        self.applayout = self._init_layout()
        
    def _init_row_descriptions(self):
        return [WidgetRowDescription(**l) for l in self.li_in]
        
    def _init_rows(self):
        return [widgets.HBox([widget, _markdown(value=f'_{des.label}_, '), _markdown(value=f'{des.name}')]) for widget, des in zip(self.li_widgets, self.li_descriptions)]
    
    def _init_layout(self):
        return widgets.VBox(self.li_rows)

    @property
    def li(self):
        [l.dict() for l in self.li_obj_ui]
        
    def _ipython_display_(self):
        display(self.applayout)

if __name__ == "__main__": 
    li = [
        {'name':'asdf','value':0, 'label':'asdf', 'options':None, 'min': None, 'max': None},
        {'name':'asdf','value':1, 'label': 'asdf', 'options':None, 'min': 1, 'max': 4},
        {'name':'asdf','value':'asdf', 'label':'asdf', 'options':['None','asdf']},
        {'name':'asdf','value':['asdf'], 'label':'asdf', 'options':['None','asdf']},
        {'name':'asdf','value':True, 'label':'asdf'},
        {'name':'asdf','value':'a string', 'label':'asdf'},
        {'name':'asdf','value':'this must be a long string over 40 characters', 'label':'asdf'},
        #{'name':'asdf','value':pd.DataFrame.from_dict({'a':[0,1], 'b': [1,2]}), 'label':'asdf'},
    ]   

    print(FloatText(**li[0]).dict())
    print(FloatSlider(**li[1]).dict())
    print(Dropdown(**li[2]).dict())
    print(SelectMultiple(**li[3]).dict())
    print(Checkbox(**li[4]).dict())
    print(Text(**li[5]).dict())
    print(Textarea(**li[6]).dict())

    

    display(EditListOfDicts(li))
# -


