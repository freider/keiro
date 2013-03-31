"""Imports all modules in current package"""
import os
import re


def is_module(filename):
    return (re.match(r".*\.py$", filename) and filename != "__init__.py")

currentdir = os.path.dirname(__file__)
module_files = filter(is_module, os.listdir(currentdir))
module_names = [os.path.splitext(m)[0] for m in module_files]

modules = [__import__(m, locals(), globals(), True) for m in module_names]
