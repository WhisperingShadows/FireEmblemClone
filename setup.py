from setuptools import setup, find_packages

setup(name='FireEmblemClone',
      version='0.1.0',
      description='A Python Fire Emblem Heroes clone',
      author='Dania M.',
      url='https://fireemblemclone.readthedocs.io/',
      packages=find_packages(include=["FireEmblemClone", "FireEmblemClone.*"]),
      py_modules=['FireEmblemCombatV2']
      )
