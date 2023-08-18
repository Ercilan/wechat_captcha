# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/15 14:49

with open(r"classes.txt") as f:
    words = f.read().rstrip()

standard_list = [chr(i) for i in range(48, 58)]
standard_list += [chr(i) for i in range(65, 91)]

words = [word.strip() for word in words.split("\n")]
print('标签列表：["' + '", "'.join(words) + '"]')
print(f'长度：{len(words)}')

words.sort()
print(words)

print([word for word in standard_list if word not in words])

# 应该没有：0 1 9 G I L O
# 可能漏了：N Q U W Z

# 实际用到 24 个字符
