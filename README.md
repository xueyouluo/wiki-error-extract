# WiKi-Error-Extract

根据wiki history数据提取纠错的平行语料。这里只提取字是1-1对齐的语料，不考虑删减字的情况。需要的话自行修改代码即可。

步骤：

1. 从wiki dumps中现在zhwiki有完整编辑历史的数据。我下载的是[20211201](https://dumps.wikimedia.org/zhwiki/20211201/)中 All pages with complete edit history (.7z)格式的数据。

2. 将所有7z文件放在同一个目录A下，在该目录下新建extracted目录。修改run/pipeline.py中对应目录地址。

3. 在A目录下运行pipeline文件。`python wiki-error-extract dir/run/pipeline.py`

4. 最终结果会在A目录下的stage5文件夹中。