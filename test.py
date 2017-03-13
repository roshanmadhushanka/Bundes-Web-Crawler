# import os
# # os.system("sudo kill `sudo lsof -t -i:9001`")
#
# import sys
# print(sys.platform)

# import urllib.parse
#
# p = 'microsoft corp'
#
# print(urllib.parse.quote_plus(p))

num = input()
if num == 0:
    print(1)
else:
    fact = 1
    for i in range(1, num + 1):
        fact *= i
    print(fact)