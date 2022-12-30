string_one_tco = '''@ndgoHODL @bamahodl @BrokenSystem20 @PeterAnsel9 @JacktheOrigin @ZiltoidXGFY @phathodl @temahkwe @DocHodllday @BitcoinOdyssey @happyclowntime @MaliVitale @jc4466 @s256anon001 @BTC_Freeborn @corndalorian @jileezie #RogueChainTip 101

.006BTC*$16875/BTC=$101.25 https://t.co/TruubYf0y8'''

string_two_tco = '''@ndgoHODL @bamahodl @BrokenSystem20 @PeterAnsel9 @JacktheOrigin @ZiltoidXGFY @phathodl @temahkwe @DocHodllday @BitcoinOdyssey @happyclowntime @MaliVitale @jc4466 @s256anon001 @BTC_Freeborn @corndalorian @jileezie #QuoteChain #StackJoin

The tip is not for the timid of heart. @AnthonyDessauer  

https://t.co/LhZcLyal4w https://t.co/P9GTRux7LT'''

string_three_tco = '''@ndgoHODL @bamahodl @BrokenSystem20 @PeterAnsel9 @JacktheOrigin @ZiltoidXGFY @phathodl @temahkwe @DocHodllday @BitcoinOdyssey @happyclowntime @MaliVitale @jc4466 @s256anon001 @BTC_Freeborn @corndalorian @jileezie #stackjoin for the this topic of morality…
?? Remnant &gt;, =, &lt; Sheepdog ??

https://t.co/uIfuXMcGtk https://t.co/VdR9kdxemG https://t.co/0ClekqLP2V https://t.co/uIfuXMcGtk https://t.co/VdR9kdxemG https://t.co/0ClekqLP2V https://t.co/uIfuXMcGtk https://t.co/VdR9kdxemG https://t.co/0ClekqLP2V https://t.co/uIfuXMcGtk https://t.co/VdR9kdxemG https://t.co/0ClekqLP2V'''


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
    
    tweet_message = tweet_message[end_of_mentions_index:len(tweet_message)]
    
    # removing //t.co addresses at end of tweet message
    if tweet_message[len(tweet_message)-23:len(tweet_message)-20] == "htt":
        tweet_message_list = [tweet_message]
        while tweet_message_list[len(tweet_message_list)-1][len(tweet_message_list[len(tweet_message_list)-1])-23:len(tweet_message_list[len(tweet_message_list)-1])-20] == "htt":
            tweet_message_list.append(tweet_message_list[len(tweet_message_list)+-1][:len(tweet_message_list[len(tweet_message_list)-1])-23].rstrip())
        tweet_message = tweet_message_list[len(tweet_message_list)-1]

    return tweet_message

# if __name__ == '__main__':
    # remove_mentions_from_tweet_message(string_one_tco)
    # remove_mentions_from_tweet_message(string_two_tco)
    # remove_mentions_from_tweet_message(string_three_tco)