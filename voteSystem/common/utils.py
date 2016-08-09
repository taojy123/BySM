#coding=utf8


from random import randint, random
import math

# def pow(a, b, c):
#     res = 1
#     while b!=0:
#         if b & 1:
#             res = (res*a) % n
#         a = (a*a) % n
#         b >>= 1
#     return res
    

# 判断一个数是否为素数
def is_prime(n):
    if n <= 3:
        return n == 2 or n == 3
    neg_one = n - 1

    s, d = 0, neg_one
    while not d & 1:
        s, d = s+1, d>>1
    assert 2 ** s * d == neg_one and d & 1

    for i in xrange(30):
        a = randint(2, neg_one)
        x = pow(a, d, n)
        if x in (1, neg_one):
            continue
        for r in xrange(1, s):
            x = x ** 2 % n
            if x == 1:
                return False
            if x == neg_one:
                break
        else:
            return False
    return True


# 随机生成一个大的素数
def randprime(N=10000):
    p = 1
    while not is_prime(p):
        p = randint(N / 10, N)
    return p


# 取两个数的乘逆元
def mod_inverse(a, b):
    # r = -1
    # B = b
    # A = a
    # eq_set = []
    # full_set = []
    # mod_set = []

    # #euclid's algorithm
    # while r!=1 and r!=0:
    #     r = b%a
    #     q = b//a
    #     eq_set = [r, b, a, q*-1]
    #     b = a
    #     a = r
    #     full_set.append(eq_set)

    # for i in range(0, 4):
    #     mod_set.append(full_set[-1][i])

    # mod_set.insert(2, 1)
    # counter = 0

    # #extended euclid's algorithm
    # for i in range(1, len(full_set)):
    #     if counter%2 == 0:
    #         mod_set[2] = full_set[-1*(i+1)][3]*mod_set[4]+mod_set[2]
    #         mod_set[3] = full_set[-1*(i+1)][1]

    #     elif counter%2 != 0:
    #         mod_set[4] = full_set[-1*(i+1)][3]*mod_set[2]+mod_set[4]
    #         mod_set[1] = full_set[-1*(i+1)][1]

    #     counter += 1

    # if mod_set[3] == B:
    #     return mod_set[2]%B
    # return mod_set[4]%B


    mod = b
    original_mod, before_mod = mod, mod
    qs = []
    while mod != 0:
        if mod != before_mod:  # skip 1st run
            # prepend rather than append so we can later just iterate over it
            qs.insert(0, int(math.floor(a / mod)))  
        before_mod = mod
        a, mod = mod, a % mod
    if before_mod != 1:     # gcd(a, mod) is not 1, thus there is no modularinverse
        raise ValueError

    s, t, qs = 0, 1, qs[1:]
    for q in qs:  # After the last run t is the solution
        s, t = t, s - (q * t)

    if t < 0:   # if t is < 0 add the modulo value to it so that it is in
                # the correct range
        t = original_mod + t

    return t
    


# 生成一对公钥私钥
def genkey():

    p = randprime()
    q = randprime()
    rand = randint(2, 10)

    ed = (p-1) * (q-1) * rand + 1

    for i in xrange(int(ed**0.5)+1, 0, -1):
        if ed % i == 0:
            e = i
            d = ed / i
            break

    n = p * q

    pubkey = (n, e)
    privkey = (p, q, d)

    return pubkey, privkey


# 获取系统公钥私钥（如果已经生成过则直接用原来的）
def get_keypair():

    open('pubkey', 'a')
    open('privkey', 'a')

    pubkey = open('pubkey').read()
    privkey = open('privkey').read()

    if pubkey and privkey:
        n, e = pubkey.split()
        p, q, d = privkey.split()

        n = int(n)
        e = int(e)
        p = int(p)
        q = int(q)
        d = int(d)

        pubkey = (n, e)
        privkey = (p, q, d)

    else:
        pubkey, privkey = genkey()
        open('pubkey', 'w').write('%d %d' % pubkey)
        open('privkey', 'w').write('%d %d %d' % privkey)

    return pubkey, privkey


# 杂凑函数
def H(m, U):
    return pow(m, U, 90) + 10


# 计算出用户应该向投票委员会发送的C
def get_C(m, U, R, pubkey):
    n, e = pubkey
    M = H(m, U)
    C = pow(R, e, n) * M % n

    return C


# 计算出投票委员会向用户返回的带上盲签名的T
def get_T(C):
    pubkey, privkey = get_keypair()
    n, e = pubkey
    p, q, d = privkey

    PinverseModQ = mod_inverse(p, q)
    QinverseModP = mod_inverse(q, p)

    m1 = pow(C, d, n) % p
    m2 = pow(C, d, n) % q

    T = (m1 * q * QinverseModP + m2 * p * PinverseModQ) % n

    return T


# 通过T计算出S
def get_S(T, R, pubkey):
    n, e = pubkey
    return mod_inverse(R, n) * T % n


# 用户验证签名有效性
def verified_by_voter(m, U, S, pubkey):
    n, e = pubkey
    return pow(S, e, n) == H(m, U)


# 投票委员会验证投票有效性
def verified_by_admin(m, U, S):
    pubkey, privkey = get_keypair()
    n, e = pubkey
    p, q, d = privkey
    return pow(H(m, U), d, n) == S


# 获取到公钥私钥，公钥展示给所有投票者，私钥只有投票委员会知道
pubkey, privkey = get_keypair()
n, e = pubkey
p, q, d = privkey

print 'n, e:', pubkey
print 'p, q, d:', privkey





if __name__ == '__main__':

    print '============= example ==================='

    # 随机生成m投票内容 U随机整数用户杂凑 R随机整数致盲因子
    m = randint(0, 100)
    U = randint(2, 100)
    R = randint(2, 100)

    print 'm:', m
    print 'U:', U
    print 'R:', R

    # 用户通过m U R 和已知的公钥,算出C,然后将C和自己的身份表示发送给投票委员会
    C = get_C(m, U, R, pubkey)

    print 'C:', C


    # 投票委员会先通过用户身份标识判断用户是否有投票资格
    # 如果有资格就通过将C和自己知道的公钥私钥一起计算,得到T,返回给用户
    # 然后将该名用户标注为已投票
    T = get_T(C, pubkey, privkey)

    print 'T:', T


    # 用户得到T后利用之前的致盲因子进行“去盲”,计算出S
    S = get_S(T, R, pubkey)

    print 'S:', S


    # 用户验证投票委员会签名的有效性,如果签名有效,下一步用户将匿名将(m, U, S)发送给投票委员会
    print verified_by_voter(m, U, S, pubkey)

    # 投票委员会验证投票有效性,如果有效,则计入选票
    print verified_by_admin(m, U, S, pubkey, privkey)

    print '====================='
    


