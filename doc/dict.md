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

# 参考文档

[Python中字典拼接的多种方法](https://www.python100.com/html/1QM8L2565PUV.html)
