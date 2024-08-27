""" 加载文档 """

import os
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain.docstore.document import Document
from typing import List


# 获取指定根目录下所有子目录的所有文件
def list_files_by_level(all_files, root_dir, level=0):
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isfile(item_path):
            # print(f"{'  ' * level}{item}")  # 使用缩进来表示目录级别
            # print("item_file:",item_path)
            all_files.append(item_path)
        elif os.path.isdir(item_path):
            # print(f"{'  ' * level}[{item}]")  # 使用方括号表示目录
            # print("item_dir:",item_path)
            list_files_by_level(
                all_files, item_path, level + 1
            )  # 递归调用，增加目录级别


# 加载指定目录的所有文件
def load_files(directory: str) -> List[Document]:
    # 1.获取directory目录下的所有文件
    all_files_list = []
    if os.path.isdir(directory):
        list_files_by_level(all_files_list, directory)
    elif os.path.isfile(directory):
        all_files_list.append(directory)
    # print("len(all_files_list):", len(all_files_list))
    # 2.把所有文件都加载
    docs = []
    for filepath in all_files_list:
        # print("Loading File:%s" % filepath)
        if filepath.lower().endswith(".txt"):
            loader = TextLoader(filepath, autodetect_encoding=True)
            docs += loader.load()
        elif filepath.lower().endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs += loader.load()
        elif filepath.lower().endswith(".docx"):
            loader = Docx2txtLoader(filepath)
            docs += loader.load()
    return docs
