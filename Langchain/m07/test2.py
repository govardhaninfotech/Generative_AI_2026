import time
# 100mb
chats = ['hello how can i help you ?',#10mb
        "i am large language model",#10mb
        "you can ask anythig..!",#10mb
        "i can give answer if posible!" #10mb
        ]

# data = 'hello how can i help you ?'
# data = "i am large language model"
# data = "you can ask anythig..!"

# range(1,10,1)
# [1,2,3,4,5,6,7,8,9,10]

def get_chat():
    for chat in chats:
        yield chat
        time.sleep(2)

get1 = get_chat()
for c in get1:
    print(c)
    
# print(next(get1))
