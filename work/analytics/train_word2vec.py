from gensim.models import word2vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = word2vec.Text8Corpus('../data/recipe_memo_wakati.txt')
model = word2vec.Word2Vec(sentences, epochs=6,vector_size=300,sg=1,min_count=5, window=5, workers=4)
model.wv.save_word2vec_format("../data/recipe_step_1_6_300_5.vec.pt", binary=True)