
import copy
from pathlib import Path

jpath = Path("test.json")

print(jpath.with_suffix(".scheme.json"))
# val = 123
# v_type = type
# print(val)
# val = v_type("978")
# print(val)

# val = None
# v_type = type(val)
# print(v_type)

# NoneType = type(None)

# print(v_type is None)
# print(issubclass(v_type, NoneType))
# print(isinstance(v_type, NoneType))
# print(issubclass(v_type, NoneType))


# l = [1,2,3,5]
# l.append(9)
# print(len(l))
# print(l)
# print(l)

# idx = l.index(2)
# # idx = 0

# for i in range(len(l)-1, idx, -1):
#     print(i, l[i])

# # del l[1]

# print(l)

# print(idx)
# print(type())

# map = {
#     "1020": {
#         "pos":{
#             "x": 0,
#             "y": 1,
#         },
#         "pos_x": 123,
#         "pos_y": 88,
        
#     },
#     "1180": {
#         "pos":{
#             "x": 8,
#             "y": 6,
#         },
#         "pos_x": 667,
#         "pos_y": 90
#     }
# }

# print(map.pop('1020'))
# # print(next(iter(map.values())))
# child_scheme = next(iter(map.values()))
# print(child_scheme)
# print(id(child_scheme))
# print(id(child_scheme['pos']))

# # shallow copy
# # new_child = child_scheme.copy()

# # deep copy
# new_child = copy.deepcopy(child_scheme)

# print(new_child)
# print(id(new_child))
# print(id(new_child['pos']))
# new_child['pos']['x'] = 555

# print("================")
# print(child_scheme)
# print(new_child)
