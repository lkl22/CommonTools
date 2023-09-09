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
## 拼接

1. 用 update() 方法拼接字典
Python提供了 update() 方法来拼接两个字典。

用法示例：
```
dict1 = {'a': 1, 'b': 2}
dict2 = {'c': 3, 'd': 4}
dict1.update(dict2)
print(dict1) # {'a': 1, 'b': 2, 'c': 3, 'd': 4}
```
update() 方法将 dict2 添加到 dict1 中，并返回一个新的字典。

2. 用 ** 运算符拼接字典
Python 3.5 版本及之后的版本可以用 ** 运算符来拼接字典。

用法示例：
```
dict1 = {'a': 1, 'b': 2}
dict2 = {'c': 3, 'd': 4}
dict3 = {**dict1, **dict2}
print(dict3) # {'a': 1, 'b': 2, 'c': 3, 'd': 4}
```
上面的代码中， ** 运算符将 dict1 和 dict2 拼接成一个新的字典。如果两个字典中存在相同的键值，则后面的字典中的值会覆盖前面的。

### Python字典拼接案例
1. 字典拼接用于参数传递
在函数调用时，我们可以用一个字典来存储参数，并将字典传递到函数中。当我们需要传递多个参数时，字典可以很好的组织这些参数。

下面是一个实例，通过拼接字典来给函数传递参数:
```
def print_info(name, age, gender):
    print('Name:', name)
    print('Age:', age)
    print('Gender:', gender)

info = {'name': 'Lucy', 'age': 23, 'gender': 'female'}
print_info(**info)
```
以上代码中，我们使用字典 info 存储参数，并通过 ** 运算符将字典传递给函数调用。这样既能让代码更加简洁，同时又能提高代码的可读性。

2. 多个字典拼接为一个大字典
当我们需要将多个字典拼接为一个大字典时，可以使用上面提到的三种拼接方法，比如:
```
dict1 = {'a': 1, 'b': 2}
dict2 = {'c': 3, 'd': 4}
dict3 = {'e': 5, 'f': 6}
dict4 = {**dict1, **dict2, **dict3}
print(dict4) # {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```
上面的代码中，我们将三个字典拼接到一个新的字典 dict4 中。

3. 拼接两个字典中的某些键值对
有时候，我们只需要拼接两个字典中的某些键值对，可以使用如下的方法：
```
dict1 = {'a': 1, 'b': 2, 'c': 3}
dict2 = {'b': 4, 'd': 5}
dict3 = {**dict1, **{k: dict2[k] for k in ['b', 'd']}}
print(dict3) # {'a': 1, 'b': 4, 'c': 3, 'd': 5}
```
以上代码中，我们只拼接了 dict1 和 dict2 中键为 'b' 和 'd' 的键值对，其他的键值对没有被拼接。

## python取字典的第一个键值

### 使用keys()和next()
```
# 定义一个字典
my_dict = {'a': 1, 'b': 2, 'c': 3}
# 使用keys()和next()获取第一个键值
first_key = next(iter(my_dict.keys()))
# 输出第一个键值
print(first_key)
```

首先，我们使用iter()函数将字典的键转换为一个迭代器（iterator）。然后，通过next()函数获取迭代器的下一个项目，即字典的第一个键。注意，由于字典是无序的，所以获取的第一个键值并不是固定的，可能会有不同的输出结果。

### 使用popitem()
popitem()方法用于随机弹出字典中的一项，并返回该项的键值对。当字典为空时，会抛出KeyError异常。我们可以利用这个方法来获取字典的第一个键值。

下面是一个使用popitem()方法获取字典第一个键值的示例代码：
```
# 定义一个字典
my_dict = {'a': 1, 'b': 2, 'c': 3}
# 使用popitem()获取第一个键值
first_key, first_value = my_dict.popitem()
# 输出第一个键值
print(first_key)
```
通过popitem()方法，我们弹出了字典中最后一个键值对（'c': 3），并将其赋值给first_key和first_value。由于字典是无序的，所以获取的第一个键值可能会有不同的输出结果。

### 使用列表解析
列表解析（List comprehension）是Python中一种简洁的创建列表的方法，我们可以借助这种方法获取字典的第一个键值。

下面是一个使用列表解析获取字典第一个键值的示例代码：
```
# 定义一个字典
my_dict = {'a': 1, 'b': 2, 'c': 3}
# 使用列表解析获取第一个键值
first_key = [key for key, value in my_dict.items()][0]
# 输出第一个键值
print(first_key)
```
在上述代码中，我们使用items()方法将字典转换为一个包含键值对的元组列表。然后，通过列表解析取出列表中的第一个键值。

需要注意的是，由于列表解析会遍历整个字典，如果字典中的键值对很多，可能会影响性能。所以，这种方法适用于键值对数量较少的情况。


## 参考文档

[Python中字典拼接的多种方法](https://www.python100.com/html/1QM8L2565PUV.html)

[python取字典的第一个键值](https://blog.51cto.com/u_16175464/6761658)
