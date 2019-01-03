#!/usr/bin/env python


#-----------------------------------------------------------------------
# twitter-trends
#  - lists the current global trending topics
#-----------------------------------------------------------------------

import string
import sys 
import re,pdb
## need to add tweepy module in Python 2.7
import tweepy
from tweepy import OAuthHandler
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier, accuracy
## need to add many_stop_words module in Python 2.7
from nltk.compat import python_2_unicode_compatible
## need to add wordcloud module in Python 2.7
from wordcloud import WordCloud
import matplotlib.pyplot as plt
#Download stopwords module
from nltk.corpus import stopwords

#-----------------------------------------------------------------------
# Defining Functions & Constants
#-----------------------------------------------------------------------

print('Program Started')

## File Initialization 

txt=open("E:\Techi\Data Science\Twitter Sentimental Analysis\corncob_lowercase.txt","r").read().lower().split() 
negative_vocab=open("E:\Techi\Data Science\Twitter Sentimental Analysis\Negative-words.txt","r").read()
positive_vocab=open("E:\Techi\Data Science\Twitter Sentimental Analysis\positive-words.txt","r").read()
neutral_vocab=open("E:\Techi\Data Science\Twitter Sentimental Analysis\Neutral-words.txt","r").read()


#positive_vocab=urllib.urlopen("http://ptrckprry.com/course/ssd/data/positive-words.txt").read()
#negative_vocab=urllib.urlopen("http://ptrckprry.com/course/ssd/data/negative-words.txt").read()

positive_vocab=positive_vocab[1535:].lower().split()
negative_vocab=negative_vocab[1540:].lower().split()
neutral_vocab=neutral_vocab.lower().split() 

stopWords = set(stopwords.words('english'))
wordcloud = WordCloud(width=480, height=480, margin=0)


## Variable Initialization

cleanseddata=[]
x_cleanseddata=[]
x_cleanseddatahashed=[]
Filters=[]
Classification=[]

Negative_words=[]
Positive_words=[]
Neutral_words=[]

test_set=[]
## Function Initialization

def word_feats(words):
    words=nltk.word_tokenize(words)
    return dict([(word, True) for word in words])
    

def remove_non_ascii(s):
    return filter(lambda x: x in  set(string.printable) , s)

def partitioner(hashtag, words):
    while hashtag:
        word_found = longest_word(hashtag, words)
       # print('yeild 1 - '+word_found)
        yield word_found
        if(word_found==''):
            word_found = longest_word_straight(hashtag, words)
           # print('yeild 2 - '+word_found)
            yield word_found
            hashtag = hashtag[:-len(word_found)]
        hashtag = hashtag[len(word_found):]

def longest_word(phrase, words):
    current_try = phrase
    #print("Gonna check : "+current_try)
#Reduce the character one by one from last
    while current_try:
        #if words are available, return available
        if current_try in words :
            #print("Reverse order Got : "+current_try)
            return current_try
        current_try = current_try[:-1]
        #print("Reduce : "+current_try)
    
    # if nothing was found, return the original phrase
    #print("Not available : "+current_try)
    return ''

def longest_word_straight(phrase, words):
    current_try = phrase
    while current_try :
        if current_try in words :
            #print("Straight order Got : "+current_try)
            return current_try
        current_try = current_try[1:]
        
    # if nothing was found, return empty
    #print("Not available : "+current_try)
    return '$' #phrase

def partition_hashtag(text, words):
    return re.sub(r'(\w+)', lambda m: ' '.join(partitioner(m.group(1), words)), text)

def Classifier_hashtag(classifier, sentence):
    # Predict
    neg = 0
    pos = 0
    neu = 0
    
    wordsFiltered = []
    
    for w in sentence.split(' '):
        if w not in stopWords:
            wordsFiltered.append(w)
    
    words=wordsFiltered
    
    for word in words:
        
        classResult = classifier.classify(word_feats(word))
        if classResult == 'Neutral' or len(word) <=2 :
            neu = neu + 1
        elif classResult == 'Positive' :
            pos = pos + 1
        elif classResult == 'Negative' :
            neg = neg + 1
        #print('Split - '+word+' : '+classResult)
        
    Positive= float(pos)/len(words)
    Negative=float(neg)/len(words)
    Neutral=float(neu)/len(words)
        
    #print('Positive: ' + str(Positive))
    #print('Negative: ' + str(Negative))
    #print('Neutral: ' + str(Neutral))
    
    if Positive==Negative or  (Neutral>=Positive and Neutral>=Negative) or sentence=='' :
        final="Neutral"
    if neg>0 :
        final="Negative"
    elif Positive>=Neutral and  Positive>=Negative :
        final="Positive"
    else :
        final='Neutral'
    
    #print('Final - '+sentence+' : '+final)
    
    
    return final
        
def wordcloud_draw(data, color = 'black'):
    words = ' '.join(data)
    cleaned_word = words
    wordcloud = WordCloud(
                      background_color=color,
                      width=2500,
                      height=2000
                     ).generate(cleaned_word)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.margins(x=1, y=0)
    plt.show()

print('Initialization is completed')
#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------

print('Accessing the tweets')

consumer_key = 'jvFpn9Modp4wRux358JclmCzB'
consumer_secret = '0aJC3RS2zIQn3sNK37Urwp5BysUd43n5kqzD1uSaQVgnpaOq5d'
access_token = '320068511-ipjNugQ3ikGLDjuDTvOh5BXjdbd6yhwaPhj82enp'
access_secret = 'Kb4VW591G5tBmGh88cZQtkDbAYbUpu9PGhI3akXH7Sd2t'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

#-----------------------------------------------------------------------
# load the twitter API via tweepy
#-----------------------------------------------------------------------
api = tweepy.API(auth)

#-----------------------------------------------------------------------
# Extracting the Trending Hashtags from twitter
#-----------------------------------------------------------------------
trendings = api.trends_place(1)
trend_list = [trend['name'] for trend in trendings[0]['trends'] ]

print('Cleansing the data')

#-----------------------------------------------------------------------
# Cleansing data in List 
#-----------------------------------------------------------------------

#Filtering the non-hashtags
#cleanseddata_0 = list(filter(lambda x: '#' in x, trend_list))
x_cleanseddata_0 = [trend_list,list(map(lambda x: True if '#' in x else False , trend_list))]

#Trimming the hash character infront of String
#cleanseddata_1 = list(map(lambda x: x.lstrip('#').lower(), cleanseddata_0)) 
x_cleanseddata_1 = [list(map(lambda x: x.lstrip('#').lower(), x_cleanseddata_0[0])) ,x_cleanseddata_0[1]]
    
#Remove the string if is it only having the numbers
#cleanseddata_2 = list(filter(lambda x: not x.isnumeric(), cleanseddata_1))
x_cleanseddata_2 = [x_cleanseddata_1[0],list(map(lambda x: True if not x.isnumeric() else False, x_cleanseddata_1[0]))]

#Trimming the non Ascii characters From String
#cleanseddata_3= list(map(lambda x: str(remove_non_ascii(x)), cleanseddata_2))
x_cleanseddata_3 = [list(map(lambda x: str(remove_non_ascii(x)), x_cleanseddata_2[0])) ,x_cleanseddata_2[1]]
 

#Trimming the Special characters From String
#cleanseddata_4= list(map(lambda x: x.strip('_').strip("'"), cleanseddata_3))
x_cleanseddata_4 = [list(map(lambda x: x.strip('_').strip("'"), x_cleanseddata_3[0])) ,x_cleanseddata_3[1]]
 
#Remove the item if is it empty
#cleanseddata_5= list(filter(lambda x: len(x.strip())>0, cleanseddata_4))
x_cleanseddata_5 = [x_cleanseddata_4[0],list(map(lambda x: True if len(x.strip())>0 else False, x_cleanseddata_4[0]))]


#-----------------------------------------------------------------------
# Spliting a hashtag to sentence
#-----------------------------------------------------------------------

print('Spliting a hashtag to sentence')


i=0
for x in x_cleanseddata_1[0] : 
    if(x_cleanseddata_5[1][i] == True and x_cleanseddata_4[1][i] == True and x_cleanseddata_3[1][i] == True and x_cleanseddata_2[1][i] == True and x_cleanseddata_1[1][i] == True ) :
        x_cleanseddatahashed.append(trend_list[i])
        x_cleanseddata.append(partition_hashtag(x, txt))
        Filters.append(True)
    i=i+1
    
FinalData=[x_cleanseddatahashed,x_cleanseddata]

print('Applying Algorithm')

#-----------------------------------------------------------------------
# Sentimental Analysis
#-----------------------------------------------------------------------

positive_features = [(word_feats(pos), 'Positive') for pos in positive_vocab]
negative_features = [(word_feats(neg), 'Negative') for neg in negative_vocab]
neutral_features = [(word_feats(neu), 'Neutral') for neu in neutral_vocab]

train_set = negative_features + positive_features + neutral_features
 
classifier = NaiveBayesClassifier.train(train_set)

i=0
for x in FinalData[1] : 
    Classification.append(Classifier_hashtag(classifier,x))
    i=i+1

Result =[FinalData[0],Classification]

print("***********************************")

i=0
for x in Result[0] : 
    if(Result[1][i]=="Negative") :
        Negative_words.append(x)
    elif(Result[1][i]=="Positive") :
        Positive_words.append(x)
    elif(Result[1][i]=="Neutral") :
        Neutral_words.append(x)
        
    print(Result[0][i] +" \t\t : "+Result[1][i])
    i=i+1
    
print("***********************************")

#-----------------------------------------------------------------------
# WordCloud
#-----------------------------------------------------------------------

print("Positive_words :")
if(len(Positive_words)>0) : wordcloud_draw(Positive_words, "White")
print("Negative_words :")
if(len(Negative_words)>0) : wordcloud_draw(Negative_words, "Black")
print("Neutral_words :")
if(len(Neutral_words)>0) : wordcloud_draw(Neutral_words, "Yellow")
