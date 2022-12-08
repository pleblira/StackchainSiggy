def remove_mentions_from_tweet_message(tweet_message):
    slices = []
    end_of_mentions_index = 0
    for index,char in enumerate(tweet_message):
        slices.append(tweet_message[index:index+2])

    if tweet_message.find("@") == 0 and tweet_message.find(" @") == tweet_message.find(" ") and tweet_message[tweet_message.find(" @")+2:len(tweet_message)].find(" @") == tweet_message[tweet_message.find(" ")+2:len(tweet_message)].find(" "):
        for index,slice in enumerate(slices):
            if slice[0] == " ":
                if slice[1] == "@":
                    # print(f"continue searching, slice: {index}, index: {index}")
                    pass
                else:
                    # print(f"found end of mentions, index: {index}")
                    # print(f"this is the slice found: {slice}")
                    end_of_mentions_index = index+1
                    break
    
    print(f"this is the sliced tweet message:\n{tweet_message[end_of_mentions_index:len(tweet_message)]}")
    return tweet_message[end_of_mentions_index:len(tweet_message)]

if __name__ == '__main__':
    remove_mentions_from_tweet_message(string5)