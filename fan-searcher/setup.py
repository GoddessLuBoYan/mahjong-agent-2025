# setup.py
from setuptools import setup, Extension

module = Extension(
    'BasicFormShanten',
    sources=['basic_form_shanten.cpp'],  # 您的 C++ 源文件
    depends=['basic_form_shanten_pywrapper.h'],
    include_dirs=[],  # 如果有额外的头文件目录，请添加
    libraries=[],     # 如果有额外的库，请添加
    extra_compile_args=['/std:c++20']  # 根据需要添加编译选项
)

setup(
    name='BasicFormShanten',
    version='1.0',
    description='Basic Form Shanten Calculator',
    ext_modules=[module],
)