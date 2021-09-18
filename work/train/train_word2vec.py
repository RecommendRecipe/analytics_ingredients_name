from gensim.models import word2vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = word2vec.Text8Corpus('../data/train/cookpad_step_corpas.txt')
model = word2vec.Word2Vec(sentences, epochs=5,vector_size=400,sg=1,min_count=5, window=8, workers=4)
model.wv.save_word2vec_format("../data/trained/cookpad_m1_v400_min5_w8.vec.pt", binary=True)