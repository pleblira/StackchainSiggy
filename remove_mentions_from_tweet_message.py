string = "@pleblira @PeterAnsel9 @BowTiedClubPro @BrokenSystem20 @fontoshi @sathoarder @derekmross @Duncan19Sard1 @GoingBlindSee @rwawoe @taodejing2 @s256anon001 @utxoset @phathodl @BitcoinIsaiah @WhereBTC @LPCapitalChi @StackchainQuant @LoKoBTC @JacktheOrigin @efebitcoin @stackysats @StakchainBuddha @yeagernakamoto @BeefSupreme14 @7noBodywins @BitcoinOdyssey @JSJumping @bryan_xrl @arshmolu @DaveAustin @FossGregfoss @MaliVitale @BitcoinBo @BTC_Freeborn @happyclowntime @JohnOdetteMD @Soverengineer @FinneJay @jc4466 @anon_orator @tertiushand @CowGalKaori #Stackjoin testing. This is a stackjoin $85 https://t.co/zq1U6yrpqS"

string2 = "@PeterAnsel9 @BowTiedClubPro @BrokenSystem20 @fontoshi @sathoarder @derekmross @Duncan19Sard1 @GoingBlindSee @rwawoe @taodejing2 @s256anon001 @utxoset @phathodl @BitcoinIsaiah @WhereBTC @LPCapitalChi @StackchainQuant @LoKoBTC @JacktheOrigin @efebitcoin @stackysats @StakchainBuddha @yeagernakamoto @BeefSupreme14 @7noBodywins @BitcoinOdyssey @JSJumping @bryan_xrl @arshmolu @DaveAustin @FossGregfoss @MaliVitale @BitcoinBo @BTC_Freeborn @happyclowntime @JohnOdetteMD @Soverengineer @FinneJay @AnthonyDessauer @jc4466 @anon_orator @tertiushand @CowGalKaori #stackjoin testing. This is not a stackjoin"

string3 = "@pleblira @PeterAnsel9 @BowTiedClubPro @BrokenSystem20 @fontoshi @sathoarder @derekmross @Duncan19Sard1 @GoingBlindSee @rwawoe @taodejing2 @s256anon001 @utxoset @phathodl @BitcoinIsaiah @WhereBTC @LPCapitalChi @StackchainQuant @LoKoBTC @JacktheOrigin @efebitcoin @StakchainBuddha @yeagernakamoto @BeefSupreme14 @7noBodywins @BitcoinOdyssey @JSJumping @bryan_xrl @arshmolu @DaveAustin @FossGregfoss @MaliVitale @BitcoinBo @BTC_Freeborn @happyclowntime @JohnOdetteMD @Soverengineer @FinneJay @AnthonyDessauer @jc4466 @anon_orator @tertiushand @CowGalKaori #stackjoin 20 https://t.co/72ChVyPpwk"

string4 = "@JacktheOrigin @WaldoVision3 @BTC_Freeborn @bamahodl @BrokenSystem20 @DocHodllday @happyclowntime @AnthonyDessauer #Stackjoin 👇 A gif for the mempool operators? https://t.co/1AzNQJM2W0"

string5 = "@itcoinPierre bitcoinpierre2 bitcoinpierre3 Pierre! Join us on #stackchain / #stackjoin next time. SHSH 🤝"

string6 = "@BowTiedClubPro @BrokenSystem20 @fontoshi @sathoarder @PeterAnsel9 @derekmross @Duncan19Sard1 @GoingBlindSee @rwawoe @taodejing2 @s256anon001 @utxoset @phathodl @BitcoinIsaiah @WhereBTC @LPCapitalChi @StackchainQuant @LoKoBTC @JacktheOrigin @efebitcoin @stackysats @StakchainBuddha @yeagernakamoto @BeefSupreme14 @7noBodywins @BitcoinOdyssey @JSJumping @bryan_xrl @arshmolu @DaveAustin @FossGregfoss @MaliVitale @BitcoinBo @BTC_Freeborn @happyclowntime @JohnOdetteMD @Soverengineer @FinneJay @AnthonyDessauer @jc4466 @anon_orator @tertiushand @CowGalKaori #stackjoin test one more time. This is not a stackjoin, gentlemen."

string7 = "@stackjoin t@test dsadsadsda "

def remove_mentions_from_tweet_message(tweet_message):
    slices = []
    end_of_mentions_index = 0
    for index,char in enumerate(tweet_message):
        slices.append(tweet_message[index:index+2])

    if tweet_message.find("@") == 0 and tweet_message.find(" @") == tweet_message.find(" ") and tweet_message[tweet_message.find(" @")+2:len(tweet_message)].find(" @") == tweet_message[tweet_message.find(" ")+2:len(tweet_message)].find(" "):
        for index,slice in enumerate(slices):
            if slice[0] == " ":
                if slice[1] == "@":
                    print(f"continue searching, slice: {index}, index: {index}")
                else:
                    print(f"found end of mentions, index: {index}")
                    print(f"this is the slice found: {slice}")
                    end_of_mentions_index = index+1
                    break
    
    print(f"this is the sliced tweet message: {tweet_message[end_of_mentions_index:len(tweet_message)]}")
    return tweet_message[end_of_mentions_index:len(tweet_message)]

if __name__ == '__main__':
    remove_mentions_from_tweet_message(string5)