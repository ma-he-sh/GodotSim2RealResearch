
arr_data = []
arr_data = [['test', 'value']]

episode=0
while True:

    arr_data.append([episode, 'somevalue=' + str(episode) ])


    if episode % 10 == 0:
        print(arr_data[:1])
        print( "before=", len(arr_data) )
        arr_data = []

        print( "after=", len(arr_data) )

    episode+=1
