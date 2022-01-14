import string
import random
import math

def construct_freq_dict(confidencedict):
  freqdict = {}
  total = 0
  for word in confidencedict:
    for char in word:
      if char in freqdict:
        freqdict[char] += 1
      else:
        freqdict[char] = 1
    total += 5
  newfreqdict = {}
  for key in freqdict:
    newfreqdict[key] = freqdict[key] / total
  sorteddict = dict({k: v for k, v in sorted(newfreqdict.items(), key=lambda item: item[1])})
  orderlist = list(sorteddict.keys())
  orderlist.reverse()
  return(sorteddict,orderlist)

def print_instructions():
  print("Welcome to wordle solver!")
  print("Here's how this works:")
  print("I'll give you the word I want you to play. You play it,\nthen enter the result from wordle by entering:")
  print("A 0 for a black tile")
  print("A 1 for a yellow tile")
  print("A 2 for a green tile")
  print("If I accidentally give you something that's not a word which\nwordle accepts, please just enter the number 3. I'll remove\nthat word from my dictionary and give you a new word.")
  print("Each guess I make will come with a percentage that represents\nhow confident I am that the word I gave is the correct answer.")
  print("Sometimes I make guesses that I know are wrong in order to\ngather information. So don't worry if I'm at\n0% confidence!")
  print("Type HELP to see these instructions again")
  print("Type QUIT to end the program")
  print()
  print("---------------------------------------")
  print()


def main():
  #freqdict, orderlist = construct_freq_dict()
  REMAINING = [x for x in string.ascii_uppercase] #letters we haven't guessed yet
  SEMIKNOWN = {} #letters that we know are in the word, but don't know position -> their possible positions with 0 for possible and 1 for impossible
  KNOWN = {} #letters we know the position of in the word -> their position 0-4
  NOT = []
  BADWORDS = []
  turn = 0
  while True:
    # print(NOT)
    # print(SEMIKNOWN)
    # print(KNOWN)
    turn += 1
    if turn > 6:
      print("Ouch, I guess I couldn't get it. Maybe next time. :(")
      print()
      print("---------------------------------------")
      print()
      break
    mostlikely,confidencedict = get_possible_words(KNOWN,SEMIKNOWN,NOT,BADWORDS)
    if len(mostlikely) == 0:
      break
    freqdict, orderlist = construct_freq_dict(confidencedict)
    mostletters = get_word_most_letters(REMAINING,freqdict,SEMIKNOWN)
    confidence = confidencedict[mostlikely]
    if turn == 6:
      if len(confidencedict) > 1:
        print("This is the last turn and I'm still not sure.")
        stringg = "It could be any of the following: "
        for worp in list(confidencedict.keys()):
          stringg += worp + ", "
        print(stringg)
        print("I'm going to reccomend you play the word " + mostlikely)
      else:
        print("Play the word " + mostlikely)
      roundedcomf = round(confidence * 100,2)
      if roundedcomf > 99.99:
        roundedcomf = 99.99
      print("(Confidence in this guess: " + str(roundedcomf) + "%)")
      bestword = mostlikely
    elif confidence > .9:
      print("Play the word " + mostlikely)
      roundedcomf = round(confidence * 100,2)
      if roundedcomf > 99.99 and not len(confidencedict) == 1:
        roundedcomf = 99.99
      print("(Confidence in this guess: " + str(roundedcomf) + "%)")
      bestword = mostlikely
    else:
      if mostletters in confidencedict:
        confidence = confidencedict[mostletters]
      else:
        confidence = 0
      print("Play the word " + mostletters)
      roundedcomf = round(confidence * 100,2)
      if roundedcomf == 100 and not confidence == 1:
        roundedcomf = 99.99
      print("(Confidence in this guess: " + str(roundedcomf) + "%)")
      bestword = mostletters
    result = verify_input()
    if result == "3":
      turn -= 1
      remove_word(bestword)
      continue
    elif result == "22222":
      print("We won!!")
      print()
      print("---------------------------------------")
      print()
      break
    elif result == "QUIT":
      exit()
    elif result == "HELP":
      print_instructions()
      break
    for letter in bestword:
      if letter in REMAINING:
        REMAINING.remove(letter)
    BADWORDS.append(bestword)
    for index in range(len(result)):
      x = result[index]
      if x == '0':
        elsewhere = False
        if bestword.count(bestword[index]) > 1:
          for index2 in range(5):
            if result[index2] in ["1","2"] and bestword[index2] == bestword[index]:
              elsewhere = True
              break
        if not bestword[index] in KNOWN and not bestword[index] in SEMIKNOWN and not elsewhere:
          NOT.append(bestword[index])
        continue
      elif x == '1':
        if bestword[index] in SEMIKNOWN:
          SEMIKNOWN[bestword[index]] = update_info(SEMIKNOWN[bestword[index]],index)
        else:
          SEMIKNOWN[bestword[index]] = update_info("00000",index)
      elif x == '2':
        if bestword[index] in KNOWN:
          KNOWN[bestword[index]].append(index)
        else:
          KNOWN[bestword[index]] = [index]
        destroy = []
        for letter in SEMIKNOWN:
          if letter == bestword[index]:
            destroy.append(letter)
          else:
            SEMIKNOWN[letter] = update_info(SEMIKNOWN[letter],index)
        for letter in destroy:
          SEMIKNOWN.pop(letter)

def verify_input():
  while True:
    this = input()
    if this in ["QUIT","3","HELP"]:
      return this
    else:
      if not len(this) == 5:
        continue
      for char in this:
        if not char in ["0","1","2"]:
          continue
      return this

def remove_word(word):
  with open("dataset.txt") as f:
    data = f.readlines()
  newlines = ""
  for line in data:
    worp = line.split(" ")[0]
    if not worp == word:
      newlines += line
  with open("dataset.txt",'w') as f:
    f.write(newlines)

def update_info(word1,pos):
  newword = ""
  for index in range(5):
    if index == pos:
      newword += "1"
    else:
      newword += word1[index]
  return newword


def get_word_most_letters(unused,freqdict,SEMIKNOWN):
  #Get the word with the 5 unused letters with the 
  #highest frequency score
  #TODO: this can be smarter, it can also look for words with semiknown letters in new positions.
  with open("dataset.txt") as f:
    data = f.readlines()
  worddict = {}
  for line in data:
    word = line[0:5]
    total = 0
    for index in range(5):
      char = word[index]
      if char in unused and char in freqdict:
        total += freqdict[char] / word.count(char)
      elif char in SEMIKNOWN:
        if SEMIKNOWN[char][index] == "0":
          total += freqdict[char] / ((1 + len(SEMIKNOWN)) * word.count(char))
    worddict[word] = total
  bestword = max(worddict, key=worddict.get)
  return bestword

def mini_check_possible(word,SEMIKNOWN):
  for letter in SEMIKNOWN:
    for position in range(5):
      if SEMIKNOWN[letter][position] == "1" and word[position] == letter:
        return False
  return True

#Gonna need dict that finds the best position for each letter.
#That's a little yikes? maybe overthinking. lets see how it performs without.
#This maybe waste of time.

def check_possible(WORD,KNOWN,SEMIKNOWN,NOT):
  for char in WORD:
    if char in NOT:
      return False
  for key in KNOWN:
    for place in KNOWN[key]:
      if not WORD[place] == key:
        return False
  for key in SEMIKNOWN:
    if not key in WORD:
      return False
  for index in range(5):
    char = WORD[index]
    if char in SEMIKNOWN:
      lookup = SEMIKNOWN[char]
      for index2 in range(len(lookup)):
        num = lookup[index2]
        if num == "1" and index2 == index:
          return False
  return True
          

def get_possible_words(KNOWN,SEMIKNOWN,NOT,BADWORDS):
  with open("dataset.txt") as f:
    data = f.readlines()
  possibles = {}
  for line in data:
    word = line[0:5]
    if word in BADWORDS:
      continue
    if not check_possible(word,KNOWN,SEMIKNOWN,NOT):
      continue
    freq = int(line.split(" ")[1])
    possibles[word] = freq
  sorteddict = dict({k: v for k, v in sorted(possibles.items(), key=lambda item: item[1])})
  orderlist = list(sorteddict.keys())
  orderlist.reverse()
  if len(orderlist) == 0:
    print("Sorry, I don't have a solution for this in my database!")
    print("If you messed up an input, you can try again.")
    print()
    print("---------------------------------------")
    print()
    return "",{}
  best = orderlist[0]
  total = 0
  for x in sorteddict:
    total += sorteddict[x]
    total += .00001
  confidencedict = {}
  for key in sorteddict:
    score = sorteddict[key] + .00001
    confidencedict[key] = score / total
  return best,confidencedict
  #get every word that it could possibly be, ranked in a 
  #dict by frequency




def choose_random_word():
  with open("dataset.txt") as f:
    data = f.readlines()
  index = random.randint(0,len(data) - 1)
  line = data[index].split(" ")
  return line[0],int(line[1])

def get_score(actual : str,guess : str):
  score = ""
  for index in range(5):
    char = guess[index]
    if actual[index] == char:
      score += "2"
    elif char in actual:
      count = actual.count(char)
      for index2 in range(5):
        char1 = actual[index2]
        char2 = guess[index2]
        if char1 == char2 and char2 == char:
          count -= 1
      if index > 0:
        usedword = guess[0:(index - 1)]
        for index2 in range(len(usedword)):
          char2 = usedword[index2]
          if char2 == char and score[index2] != "2":
            count -= 1
      if count > 0:
        score += "1"
      else:
        score += "0"
    else:
      score += "0"
  return score

def record_score(win : bool, freq, interval,turn):
  adjustedfreq = freq / 100
  if win:
    amount = (1/(adjustedfreq + 1)) * math.sqrt(36 - (turn ** 2))
  else:
    if freq == 0:
      amount = 0
    else:
      amount = -6
  with open("scores2.tsv") as f:
    data = f.readlines()
  newfile = ""
  found = False
  for line in data:
    tonk = line.split("\t")
    thisint = int(tonk[0])
    if thisint == interval:
      current = float(tonk[1].replace("\n",""))
      current += amount
      wins = int(tonk[2])
      wins += 1 if win else 0
      turns = int(tonk[3])
      turns += turn
      newfile += str(interval) + "\t" + str(current) + "\t" + str(wins) +  "\t" + str(turns) + "\n"
      found = True
    else:
      newfile += line
  if not found:
    newfile += str(interval) + "\t" + str(amount) + "\t1\t" + str(turn) + "\n"
  with open("scores2.tsv","w") as f:
    f.write(newfile)

def run_test(interval,word : str,freq):
  #pick a word at random
  #the interval determines whether it picks an informative guess or a 
  REMAINING = [x for x in string.ascii_uppercase] #letters we haven't guessed yet
  SEMIKNOWN = {} #letters that we know are in the word, but don't know position -> their possible positions with 0 for possible and 1 for impossible
  KNOWN = {} #letters we know the position of in the word -> their position 0-4
  NOT = []
  BADWORDS = []
  turn = 0
  trueinterval = interval / 100
  while True:
    turn += 1
    if turn > 6:
      record_score(False,freq,interval,turn)
      break
    mostlikely,confidencedict = get_possible_words(KNOWN,SEMIKNOWN,NOT,BADWORDS)
    if len(mostlikely) == 0:
      print("something has gone wrong")
      exit()
    freqdict, orderlist = construct_freq_dict(confidencedict)
    mostletters = get_word_most_letters(REMAINING,freqdict,SEMIKNOWN)
    confidence = confidencedict[mostlikely]
    if confidence > trueinterval or turn == 6:
      bestword = mostlikely
    else:
      bestword = mostletters
    result = get_score(word,bestword)
    if result == "22222":
      record_score(True,freq,interval,turn)
      break
    for letter in bestword:
      if letter in REMAINING:
        REMAINING.remove(letter)
    BADWORDS.append(bestword)
    for index in range(len(result)):
      x = result[index]
      if x == '0':
        elsewhere = False
        if bestword.count(bestword[index]) > 1:
          for index2 in range(5):
            if result[index2] in ["1","2"] and bestword[index2] == bestword[index]:
              elsewhere = True
              break
        if not bestword[index] in KNOWN and not bestword[index] in SEMIKNOWN and not elsewhere:
          NOT.append(bestword[index])
        continue
      elif x == '1':
        if bestword[index] in SEMIKNOWN:
          SEMIKNOWN[bestword[index]] = update_info(SEMIKNOWN[bestword[index]],index)
        else:
          SEMIKNOWN[bestword[index]] = update_info("00000",index)
      elif x == '2':
        if bestword[index] in KNOWN:
          KNOWN[bestword[index]].append(index)
        else:
          KNOWN[bestword[index]] = [index]
        destroy = []
        for letter in SEMIKNOWN:
          if letter == bestword[index]:
            destroy.append(letter)
          else:
            SEMIKNOWN[letter] = update_info(SEMIKNOWN[letter],index)
        for letter in destroy:
          SEMIKNOWN.pop(letter)


def determine_best_interval():
  with open("scores2.tsv",'w') as f:
    f.close() #scores goes interval,score,wins
    #wins are out of 100
  words = {}
  for guess in range(200):
    word,freq = choose_random_word()
    words[word] = freq
  for inter in range(16):
    interval = 25 + (5 * inter)
    for word in words:
      print("Guessing " + word + " with interval " + str(interval))
      run_test(interval,word,words[word])

print_instructions()
while True:
  main()
#determine_best_interval()