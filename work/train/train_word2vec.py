from gensim.models import word2vec
import logging
<<<<<<< HEAD

sentences = word2vec.Text8Corpus('../data/train_data/rakuten_scray_train.txt')

for size in range(4,6):
    size *= 100
    saved_path = "../data/trained_data/rakuten_m1_v" + str(size) + "_min5_w4.vec.pt"
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    model = word2vec.Word2Vec(sentences, epochs=5,vector_size=size,sg=1,min_count=5, window=4, workers=8,hs=0)
    model.wv.save_word2vec_format(saved_path, binary=True)
=======
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = word2vec.Text8Corpus('../data/train_data/recipe_train.txt')
model = word2vec.Word2Vec(sentences, epochs=100,vector_size=500,sg=1,min_count=5, window=4, workers=8,hs=0)
model.wv.save_word2vec_format("../data/trained_data/cookpad_m1_v500_min5_w4.vec.pt", binary=True)
>>>>>>> ab7382e0371a54d7bad72daf7387e88c7dd2aa49
