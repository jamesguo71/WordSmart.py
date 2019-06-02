import re
import stardict
import sys
import time
from collections import OrderedDict

class BooKnowledge:
    def __init__ (self, filepath, threshold=0):
        self.dbname = "stardict.db"
        self.filepath = filepath
        self.sd = stardict.StarDict(self.dbname)
        self.lemma = stardict.LemmaDB()
        self.lemma.load('lemma.en.txt')
        self.worddict = OrderedDict()
        self.threshold = threshold
        self.find_uncapword_sent=False
        self.myvocab = [line.split("\t")[0] for line in open("myvocab.txt", 'r').read().split('\n') 
                                     if not line.startswith("#")]

    def run(self):
        text = open(self.filepath, "r").read()
        sent_list = self.split_into_sentences(text)
        for linenum, line in enumerate(sent_list, 1):
            print("Line num: %d \r"%linenum, end="")
            if line.startswith('"'): line = "'" + line
            for _, _ in self.word_lookup(line):
                pass
        self.write2file()

    def write2file(self):
        stime = time.strftime("_output_%M%S",time.localtime())
        fo = open(self.filepath + stime + ".txt", "w")
        for k in self.worddict:
            if len(self.worddict[k]) > 2:
                fo.write(k + "\t[" + self.worddict[k][2].strip() + "]\t"
                    + self.worddict[k][3] + "\t" 
                    + self.worddict[k][4].strip() + "\n")
        fo.close()

    def split_into_sentences(self, text):
        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = r"(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub(r"\s" + alphabets + "[.] ",r" \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        for s in sentences:
            yield s.strip()

    def sent_lemmatize(self, line):
        wordlist_ori = re.compile(r'[^A-Za-z-]+').split(line)
        for word in wordlist_ori:
            try:
                word = re.match(r"^-?([\w-]+?)-?$", word).group(1) #去除单词首尾为-的情况
            except:
                pass
            stem = self.lemma.word_stem(word.lower())
            if stem:
                lemma = stem[0].lower()
            else:
                lemma = word.lower()
            yield word, lemma

    def is_valid_entry(self, word, lemma, line):
        sdresult = self.sd.query(lemma)
        if (sdresult != None):    
            phonetic = sdresult['phonetic']
            # ignore english definitions for now
            # expl = (sdresult["translation"] + ";" + sdresult["definition"]).replace("\n", "")
            expl = (sdresult["translation"]).replace("\n", "")
            freq = sdresult['frq'] + sdresult['bnc'] #ecdict assures 'frq' and 'bnc' have values
            cap = True if word.istitle() else False
            if (lemma not in self.worddict) \
                and not (phonetic == "" and word.istitle()) \
                and not (phonetic == "" and word.isupper()) \
                and not (phonetic == "" and expl.startswith("[网络]")) \
                and not (phonetic == "" and expl.startswith("[计]")) \
                and not (phonetic == "" and expl.startswith("abbr")):
                if sdresult['frq'] and sdresult['bnc']:
                    freq = freq//2
                self.worddict[lemma] = [word, freq, phonetic, expl, line, cap]
                if freq >= self.threshold:
                    return True
            elif lemma in self.worddict and self.find_uncapword_sent:
                # update existing item when explicitly looking for line with an "uncapped" new word
                if (self.worddict[lemma][5] is True) and (not word.istitle()):
                    self.worddict[lemma] = [word, freq, phonetic, expl, line, cap]
        return False

    def is_known(self, lemma, word):
        return (lemma in self.myvocab) or (word in self.myvocab)

    def word_lookup(self, line):
        for word, lemma in self.sent_lemmatize(line):
            if (not self.is_known(lemma, word)) and self.is_valid_entry(word, lemma, line):
                yield lemma, self.worddict[lemma]
    
if __name__ == '__main__':
    try:
        filepath = sys.argv[1]
    except:
        print("Usage: python3 luokepy3.py filepath\n")
        exit()
    bk = BooKnowledge(filepath)
    bk.run()
