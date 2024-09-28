#!/bin/bash

# 检查参数，确保提供了文件夹路径
if [ "$#" -ne 1 ]; then
    echo "使用方法: $0 <文件夹路径>"
    exit 1
fi

# 保存文件夹路径
directory=$1

# 检查提供的路径是否确实是文件夹
if [ ! -d "$directory" ]; then
    echo "错误：提供的路径不是一个文件夹"
    exit 1
fi

# 遍历文件夹中的所有文件（包括隐藏文件）
echo "文件夹 $directory 的结构："
for file in "$directory"/* "$directory"/.*; do
    if [ -e "$file" ]; then
        echo "$(basename "$file")"
    fi
done
