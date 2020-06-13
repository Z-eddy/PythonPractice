m = {"key0": 123, "key1": "test"}
va0 = m.get("key2", 88)  # 当没有的时候使用默认值88
print(m)
m.setdefault("key3", "defaultValue")  # 有则不生效,无则生效
print(m)
