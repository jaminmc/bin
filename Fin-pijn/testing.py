test1 = 1

def testing():
    test1 = 999
    test2 = 999
    print('test1: ', test1)
    
def testing2():
    test2 = 222
    print('test2-before: ', test2)
    testing()
    print('test2-after: ', test2)
testing()

print('test1after: ', test1)
testing2()
print('test1after2: ', test1)



