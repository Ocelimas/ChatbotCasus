from apiclient.discovery import build 
import nltk, os, json, time, Data
import numpy as np
import re
from collections import Counter
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

#nltk.download('punkt')
# probability threshold
ERROR_THRESHOLD = 0
# load our calculated synapse values
synapse_file = 'brain.json'

# compute sigmoid nonlinearity
def sigmoid(x):
    output = 1/(1+np.exp(-x))
    return output

# convert output of sigmoid function to its derivative
def sigmoid_output_to_derivative(output):
    return output*(1-output)
 
def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

def think(sentence, words, show_details=False):
    x = bow(sentence.lower(), words, show_details)
    if show_details:
        print ("sentence:", sentence, "\n bow:", x)
    # input layer is our bag of words
    l0 = x
    # matrix multiplication of input and hidden layer
    l1 = sigmoid(np.dot(l0, synapse_0))
    # output layer
    l2 = sigmoid(np.dot(l1, synapse_1))
    return l2

def OpenFile():
    with open(synapse_file) as data_file: 
        synapse = json.load(data_file) 
        synapse_0 = np.asarray(synapse['synapse0']) 
        synapse_1 = np.asarray(synapse['synapse1'])


        print("TrainingData geladen")
        return synapse, synapse_0, synapse_1
    
def classify(sentence, words, classes, show_details=False):
    results = think(sentence, words, show_details)
    try:
        results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD ]
        if len(results) > 0:
            results.sort(key=lambda x: x[1], reverse=True) 
            return_results =[[classes[r[0]],r[1]] for r in results]
            answerToQuestion = Data.GetAnswer(return_results[0][0])
            print ("\n Vraagnummer: %s \n Zekerheid: %s%%" % (return_results[0][0], return_results[0][1]))
            print("\n\n answer to question: \n\n ")
            print(str(answerToQuestion))
        else:
            print("Kan de taal niet met zekerheid bepalen...")
    except Exception, e:
        print("Kaput: %s" % e)


synapse, synapse_0, synapse_1 = OpenFile()


#returns translate sentence
def g_translate(source):
    service = (build('translate', 'v2', developerKey='AIzaSyB0x83parhwESgG8Ig8jhN5ZA34_VVyn8Q'))
    request = service.translations().list(q=source, target='en')
    response = request.execute()
    return response['translations'][0]['translatedText']


while True:
    print("\n"+"#"*40)
    tempinput = raw_input("Type een zin:\n")
    tempinput = g_translate(tempinput)
    print "Engels:", tempinput
    classify(str(tempinput), synapse['words'], synapse['classes'], show_details=False)
