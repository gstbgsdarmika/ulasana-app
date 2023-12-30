import string
import regex as re
import pandas as pd 
from sklearn.utils import resample
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemover, ArrayDictionary
def remove_emojis(text):
    return str(text.encode('ascii', 'ignore'))

def remove_punctuation(text):
    # Make a regular expression that matches all punctuation
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    # Use the regex
    return regex.sub(' ', text)

# stopwords removal
stopword_factory = StopWordRemoverFactory()
stopword = stopword_factory.create_stop_word_remover()
def remove_stopwords_sastrawi(text):
    return stopword.remove(text)

# stemming
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()
def stem_words(text):
    return stemmer.stem(text)

# normalisasi kata tidak baku
slang_dict = pd.read_csv('dataset/normalization.csv', encoding='latin-1', header=None)
slang_dict = slang_dict.rename(columns={0: 'original', 1: 'replacement'})
slang_dict_map = dict(zip(slang_dict['original'], slang_dict['replacement']))
def normalize_slang(text):
    return ' '.join([slang_dict_map[word] if word in slang_dict_map else word for word in text.split(' ')])

def preprocess(text):
    if text is None or not isinstance(text, str):
        return ""

    text1 = text.lower()   # case folding
    text5 = re.sub(r"\d+", "", text1)   # remove numbers
    text6 = text5.replace('\\n',' ')    # hapus karakter '\n'
    text7 = remove_punctuation(text6)
    text8 = normalize_slang(text7)
    text9 = stem_words(text8)
    text10 = remove_stopwords_sastrawi(text9)
    result = text10.strip()   # remove whitespace
    return result

def returnSentiment(score):
    if (score >= 4):
        return "positive"
    elif (score <= 3):
        return "negative"