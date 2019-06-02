# 洛克生词本
这个小程序可以帮助你识别一篇文字中你不认识的那些单词，并给出发音、解释和例句。
工作原理是，识别每个单词的原型，并过滤掉你在myvocab文件中已输入的单词。

最开始的目的是作者希望导入这样的形式到Anki中学习，
但现在推荐你使用“不背单词”app的自定义词书功能，导入这些单词进行学习。


环境要求：

    请使用python3.7环境（如果你是之前的用户，请卸载python2.7或升级到python3.7)。
    这个程序需要终端环境，对于Windows是cmd，对于Mac是“终端”程序。


内含文件介绍：

    freq_list文件是一个精心挑选的词频列表，一般来说越靠前的词越简单
    myvocab文件是你“已经熟悉”的单词，默认只添加了简单的星期词和示例简单词

> 建议你根据freq_list筛选出一份你已经熟悉的单词，把这些熟悉的单词放到myvocab文件中
    
    stardict和startdict.db
    
    stardict.py和startdict.db，以及lemma.en.txt，是使用的skywind3000的开源词典：
    https://github.com/skywind3000/ECDICT

程序运行方法：

    如果你的文件在当前目录下，假设文件名为filename，那么在终端中运行：
    python luokepy3.py filename
    (如果运行不成功，试试python3 luokepy3.py filename)

    最终生成的文件是filename_output_***.txt，跟你需要查询的文件在同一个文件目录下。



