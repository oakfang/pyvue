from setuptools import setup

setup(name='pyvue',
      version='0.1.7',
      description='Generate HTML strings in pure python, or JSX style code',
      url='http://github.com/oakfang/pyvue',
      author='Alon Niv',
      author_email='oakfang@gmail.com',
      license='MIT',
      packages=['pyvue'],
      entry_points={
        "console_scripts": [
            "pyvuec = pyvue.parser:compile_file"
        ]
      })