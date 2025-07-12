from setuptools import setup, Extension
import os

# 定义编译参数
module = Extension(
    name='judge_lib',
    sources=['judge_lib.cpp'],  # 替换为您的C++源文件
    include_dirs=[
        r'D:\includes\JsonCPP_modified2',  # 你的JsonCPP_modified2 cpp库路径
        r'D:\includes\boost_1_84_0\boost_1_84_0',  # 你的boost库路径
        r'.'  # 当前路径，用于将judge_lib.h纳入编译范围
    ]
)

# 配置setup
setup(
    name='judge_lib',
    version='1.0',
    description='Custom C++ extension for Python',
    ext_modules=[module]
)