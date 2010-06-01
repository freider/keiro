"""Imports all modules in current package"""
import os
import re

def is_module(filename):
	return (re.match(r".*\.py$", filename) and filename != "__init__.py")

currentdir = os.path.dirname(__file__)
modules = filter(is_module, os.listdir(currentdir))

__all__ = [os.path.splitext(m)[0] for m in modules]