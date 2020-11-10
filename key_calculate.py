def polycreate(values, key):
    H = values
    newk = key
    if len(H) > 0:
        accesscontrol = [1, -H[0]]
        for i in range(1, len(H)):
            tmp = accesscontrol.copy()
            for j in range(1, len(accesscontrol)):
                accesscontrol[j] += -1*H[i]*tmp[j-1]
            accesscontrol.append(-1*tmp[len(accesscontrol)-1] * H[i])
    else:
        accesscontrol = [1]
    accesscontrol[-1] += newk
    return accesscontrol


def group_session_key_calculation(vector, value):
    # 计算群会话密钥
    # 访问控制多项式构造方式为 f(x) = (x-hash(s0,z))(x-hash(s1,z))...(x-hash(sn,z))+k
    # 考虑访问控制多项式 f(x)=a0x^n+a1x^(n-1)+...+an 的存储方式为 [a0,a1,...,an]
    # 此时只需令 x = hash(si,z) 带入计算即可得到群会话密钥 k 的值
    group_session_key = vector[-1]
    hash_num = value
    for i in range(1, len(vector)):
        group_session_key += vector[-(i+1)]*pow(hash_num, i)
    return group_session_key


# 构造 f(x) = (x-1)(x-3)(x-5)(x-7)(x-9)+100
values = [1, 3, 5, 7, 9]
key = 100
accesscontrol = polycreate(values, key)
print("While f(x) = (x-1)(x-3)(x-5)(x-7)(x-9)+100")
print("Correct key:")
for value in values:
    print("f({})".format(value)+" =",
          group_session_key_calculation(accesscontrol, value))
print("Error key:")
error_values = [2, 4, 6, 8, 10]
for value in error_values:
    print("f({})".format(value)+" =",
          group_session_key_calculation(accesscontrol, value))
