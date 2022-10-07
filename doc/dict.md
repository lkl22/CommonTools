# 字典

## 遍历

1、for循环遍历：使用for循环直接遍历字典。

此时得到字典的key值。

2、keys()：用于获取字典的key值。

获得的类型是dict_keys，然后使用list()进行强制转换，获得key值，或者使用for循环遍历。

3、values()：用于获取字典的values值。

类型为dict_values，然后使用list()强制转换，获取values值，也可以使用for循环遍历。

4、items()：用于获取字典中的所有键值对。

获得的类型是dict_items，内容是由key值和value值组成的元组类型。

```python
# 定义一个字典
dic = {'Name': '张三', 'Gender': '男', 'Age': 20, 'Height': 177}
# for 循环遍历字典内容
for i in dic:
    print(i, ' : ', dic[i])
print('===' * 26)

# dic.keys 遍历
print(type(dic.keys()))   # 打印 dic.keys() 得到的数据类型
for i in dic.keys():
    print(i, ' : ', dic[i])
print('===' * 26)

# dic.values() 遍历
print(type(dic.values()))
for i in dic.values():
    print(i)
print('===' * 26)

# dic.items() 遍历
print(dic.items())
for i in dic.items():   # 使用二次循环进行遍历，第一次获得元组的内容，第二次获得具体的值
    for j in i:
        print(j, end=' : ')
    print()
```

