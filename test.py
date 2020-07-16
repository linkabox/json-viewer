
l = [1,2,3,5]
print(l)

idx = l.index(2)
# idx = 0

for i in range(len(l)-1, idx, -1):
    print(i, l[i])

# del l[1]

print(l)

# print(idx)
# print(type())