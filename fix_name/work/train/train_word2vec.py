from gensim.models import word2vec
import logging

sentences = word2vec.Text8Corpus('../data/train_data/recipe_train.txt')

loss_file = open("./compute_loss.csv", 'w')

vector_size = 250

for size in range(1,11):
    vector_size += 10*size 
    saved_path = "../data/trained_data/recipe_m1_v" + str(vector_size) + "_min5_w4.vec.pt"
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    model = word2vec.Word2Vec(sentences, epochs=5,vector_size=size,sg=1,min_count=5, window=4, workers=8,hs=0)
    loss_file.write(str(vector_size) + "," + str(model.get_latest_training_loss()) + "\n")
    model.wv.save_word2vec_format(saved_path, binary=True)
loss_file.close()