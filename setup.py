from setuptools import find_packages, setup
from typing import List

c='-e .'
def function(file_path:str)->List[str]:
    '''this function return list of requirements '''
    requirements=[]
    with open(file_path) as file:
        requirements=file.readlines()
        '''when we read lines , \n also come , to remove that we use below code'''
        requirements=[i.replace('\n','') for i in requirements]
        
        if c in requirements:  # we dont want -e. here , so we remove it
            requirements.remove(c)
    return requirements

setup(
    name='Drug Review Analytics & Insights Platform',
    version='0.0.1',
    author='Nirabhay Singh Rathod',
    author_email='nirbhay105633016@gmail.com',
    packages=find_packages(),
    install_requires=function('requirements.txt')
)