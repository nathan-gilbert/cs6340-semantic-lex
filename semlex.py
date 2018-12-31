#semlex.py

# This is an implmentation of a semantic lexical generation algorithm. More
# specifically this is a hybrid of the Riloff/Sheppard & Charniak/Roark
# algorithm.
import sys
import string
from copy import deepcopy

class Phrase:
    def __init__(self, l="", r=""):
        self.lhs = l
                self.rhs = r

        def getRHS(self):
            return self.rhs

        def getLHS(self):
            return self.lhs

        def __str__(self):
            return "%s -> %s" % (self.lhs, self.rhs)

# This function sorts the score list first by it's score ( which is the # of collactions with C over it's overall frequency.)
# If there is a tie, it nexts sorts by overall frequency of the word, then if there is a tie again it sorts by alphabet.
def sortScores(x,y):
    #Here sortScores is passed two tuples, x and y, with the makeup (score, word, frequency)

        if x[0] < y[0]:
            return -1
        elif x[0] > y[0] :
            return 1
        else:
            if x[2] < y[2]:
                return -1
            elif x[2] > y[2]:
                return 1
            else:
                if x[1] > y[1]:
                    return -1
                else:
                    return 1
        return 0

def main(args):
    """Semlexer at work. Where the magic happens. """

        if len(args) < 2:
            print "usage: semlex <seedsfile> <corpusfile>"
                sys.exit(0)

        seeds = open(args[0], 'r')

        semanticCat = ""					#The semantic category for this semlexer.
        dictionary = []					#The current dictionary of words.
        sentenceList = []					#This sentence lists holds lists of phrases, where each
                                                                                        #sublist is a sentence.

        wordList = []						#This holds the freq of all words in corpus.

        initList = list(seeds)

        seeds.close()

        semanticCat = string.lower(initList[0].strip())
        del initList[0]
        initList = map(string.lower, map(string.strip, initList))
        dictionary = initList

        #initial printouts
        strbuf = ""
        for i in dictionary:
            strbuf += i + " "
        print "SEMANTIC CATEGORY: %s\nSEED WORDS: %s" % (semanticCat, strbuf.strip())

        #opening corpus file.
        corpus = open(args[1], 'r')

        #getting frequency counts, organizing sentences.
        i = 0
        phraseType = ""
        words = []
        curSent = []															#The current sentence being created.
        freqList = {}															#A dictionary for keeping track of frequency of each word. The key is the
                                                                                                                                                                #word, but the value is a 1x2 array, where the first element is the frequency
                                                                                                                                                                #and the second element is a string holding all the sentences this word
                                                                                                                                                                #appears in.

        #Looking through the lines of the corpus to try and make some sense, i.e., sentences and phrases
        #from the tags.
        for line in corpus:
            tmp = line.split(":") 														#A temp list to hold the split line.
                phraseType = string.lower(tmp[0].strip())								#The left hand side of a phrase. (it's POS)
                words = map(string.strip, map(string.lower, tmp[1].split()))	#The righ hand side of a phrase. (the words...)
                p = Phrase(phraseType, words)												#Phrase datatype (see above).
                curSent.append(deepcopy(p))

                #Adding to the frequency chart.
                for w in words:
                    if not freqList.has_key(w):
                        freqList[w] = [1.0, str(i)]
                    else:
                        update = freqList[w]
                                update = [update[0] + 1, update[1] + " " + str(i)]
                                freqList[w] = deepcopy(update)

                        if w.strip() == '<eos':
                            i = i + 1															#keeping track of what sentence we are on.
                                sentenceList.append(deepcopy(curSent))
                                curSent = []

        corpus.close()
        sentences = []
        co = False

        #All preliminary work done, time to start working...
        for i in range(0,8):
            scoreList = {}																	#dictionary of scores per iteration.
                collocate = {}																	#dictionary of collocated words.

                for key in freqList.keys():

                    if (freqList[key][0] >= 3.0) and (not key in dictionary):
                        sentences = map(lambda x: int(x), freqList[key][1].split())

                                #Removing any duplicate sentences (sentence where 'key' appears twice.) The reason for this is third loop (*)
                                #from here will catch any duplicate occurances of a word in this setence.
                                dups = {}
                                for x in sentences:
                                    dups[x] = x

                                sentences = dups.values()

                                for index in sentences:

                                    sent_w = sentenceList[index]					#Sentence were word with frequency >= 3 is found.
                                        index_w = 0

                                        #(*)
                                        for phrase_w in sent_w:

                                            #w is a head noun:
                                                        if phrase_w.getRHS()[-1] == key and (phrase_w.getLHS() == "np" or phrase_w.getLHS() == "pp"):
                                                            index_w = sent_w.index(phrase_w)
                                                                index_d = 0

                                                                #checking for corresponding dicitionary word.
                                                                for phrase_d in sent_w:
                                                                    if phrase_d.getRHS()[-1] in dictionary and (phrase_d.getLHS() == "np" or phrase_d.getLHS() == "pp"):
                                                                        index_d = sent_w.index(phrase_d)

                                                                                co = False
                                                                                begin = min(index_w, index_d) + 1
                                                                                end = max(index_w, index_d)

                                                                                middleGround = sent_w[begin:end]

                                                                                for item in middleGround:

                                                                                    if item.getLHS() == "np" or item.getLHS() == "pp":
                                                                                        co = False
                                                                                                break						#This break will catch scenairos like word/seed/word and make sure
                                                                                            #they are only counted once.

                                                                                        if "word" in item.getLHS() and (">comma" in item.getRHS() or "and" in item.getRHS() or "or" in item.getRHS()):
                                                                                            co = True

                                                                                if co:
                                                                                    if not collocate.has_key(phrase_w.getRHS()[-1]):
                                                                                        collocate[phrase_w.getRHS()[-1]] = 1.0
                                                                                    else:
                                                                                        update = collocate[phrase_w.getRHS()[-1]] + 1.0
                                                                                                collocate[phrase_w.getRHS()[-1]] = deepcopy(update)
                                                                                        break
                                                                if co:
                                                                    co = False
                                                                        break
                for k in collocate.keys():
                    scoreList[k] = collocate[k]/freqList[k][0]

                #sort words by value...etc.
                sortedScoreList = [(scoreList[key], key, int(freqList[key][0])) for key in scoreList.keys()]
                sortedScoreList.sort(sortScores)

                # if you want most frequent first
                sortedScoreList.reverse()

                # plain printout
                print
                print "*** ITERATION %d ***" % (i+1)
                for score, word,frequency in sortedScoreList[0:5]:
                    print "Selecting: %s SCORE=%6f FREQ=%d" % (word,score,frequency)

                #add words top 5 words to dictionary.
                for i in sortedScoreList[0:5]:
                    dictionary.append(i[1])
                        del freqList[i[1]]


#Main function of program.
main(sys.argv[1:])
