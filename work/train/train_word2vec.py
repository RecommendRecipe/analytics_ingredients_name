from gensim.models import word2vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = word2vec.Text8Corpus('../data/train_data/recipe_train.txt')
model = word2vec.Word2Vec(sentences, epochs=100,vector_size=500,sg=1,min_count=5, window=4, workers=8,hs=0)
model.wv.save_word2vec_format("../data/trained_data/cookpad_m1_v500_min5_w4.vec.pt", binary=True)