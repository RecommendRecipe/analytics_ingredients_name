from gensim.models import word2vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = word2vec.Text8Corpus('../data/recipe_memo_wakati.txt')
model = word2vec.Word2Vec(sentences, min_count=20, window=15)
model.wv.save_word2vec_format("../data/recipe_step15.vec.pt", binary=True)