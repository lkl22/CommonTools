# 数据排序

## 字典排序方法

> sorted(iterable, key=None,reverse=False)

参数说明：
* iterable：可迭代对象，即可以用for循环进行迭代的对象；
* key：主要是用来进行比较的元素，只有一个参数，具体的函数参数取自于可迭代对象中，用来指定可迭代对象中的一个元素来进行排序；
* reverse：排序规则，reverse=False升序(默认)，reverse=True降序。

### 单个字典格式数据排序
```python
# 字典排序
a = {'a': 3, 'c': 89, 'b': 0, 'd': 34}
# 按照字典的值进行排序
a1 = sorted(a.items(), key=lambda x: x[1])
# 按照字典的键进行排序
a2 = sorted(a.items(), key=lambda x: x[0])
print('按值排序后结果', a1)
print('按键排序后结果', a2)
print('结果转为字典格式', dict(a1))
print('结果转为字典格式', dict(a2))
```

原理：以a.items()返回的列表[(‘a’, 3), (‘c’, 89), (‘b’,0), (‘d’, 34)]中的每一个元素，作为匿名函数(lambda)的参数，x[0]即用“键”排序，x[1]即用“值”排序；返回结果为新的列表，可以通过dict()函数转为字典格式。

### 字典列表排序
```python
b = [{'name': 'lee', 'age': 23}, {'name': 'lam', 'age': 12}, {'name': 'lam', 'age': 18}]
b1 = sorted(b, key=lambda x: x['name'])
b2 = sorted(b, key=lambda x: x['age'],  reverse=True)
b3 = sorted(b, key=lambda x: (x['name'], -x['age']))
print('按name排序结果：', b1)
print('按age排序结果：', b2)
print('name相同按age降序排列：', b3)
```

原理：以列表b里面的每一个字典元素作为匿名函数的参数，然后根据需要用键取字典里面的元素作为排序的条件，如x[‘name’]即用name键对应的值来排序。
