            t = Template(openfile.read())
            vals = stackjoin_tweets_table_data
        with open('stackjoin_tweets/stackjoin_tweets.html') as f:
            f.write(t.render(vals))
