import sys
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.svm import LinearSVC

sentences_dir = sys.argv[1]
labels_train_dir = sys.argv[2] # projected
labels_test_dir = sys.argv[3] # original
list_tags_file = sys.argv[4]
list_train_file = sys.argv[5]
list_test_file = sys.argv[6]
max_ngrams = int(sys.argv[7])
use_tfidf = int(sys.argv[8])
predictions_save_file = sys.argv[9]
labels_save_file = sys.argv[10]
if len(sys.argv) > 11:
    embeddings_dir = sys.argv[11]
else:
    embeddings_dir = None

sentences = {}
labels = {}

list_train = []
list_test = []
list_all = []

list_target_tags = []

with open(list_tags_file) as f:
    for line in f:
        values = line.strip().split(" ")
        for v in values:
            list_target_tags.append(v)

with open(list_train_file) as f:
    for line in f:
        list_train.append(line.strip())
        list_all.append(line.strip())

with open(list_test_file) as f:
    for line in f:
        list_test.append(line.strip())
        list_all.append(line.strip())

for item in list_train:
    sentences[item] = []
    labels[item] = []
    with open(os.path.join(sentences_dir,item)) as f:
        for line in f:
            sentences[item].append(line.strip())
    with open(os.path.join(labels_train_dir,item)) as f:
        for line in f:
            label = 0
            tags = line.strip().split()
            for tag in tags:
                if tag in list_target_tags:
                    label = 1
            labels[item].append(label)

for item in list_test:
    sentences[item] = []
    labels[item] = []
    with open(os.path.join(sentences_dir,item)) as f:
        for line in f:
            sentences[item].append(line.strip())
    with open(os.path.join(labels_test_dir,item)) as f:
        for line in f:
            label = 0
            tags = line.strip().split()
            for tag in tags:
                if tag in list_target_tags:
                    label = 1
            labels[item].append(label)

documents_id_train = []
sentences_train = []
sentences_test = []
labels_train = []
labels_test = []

count_documents = 0
for item in list_train:
    for s in sentences[item]:
        sentences_train.append(s)
        documents_id_train.append(count_documents)
    for l in labels[item]:
        labels_train.append(l)
    count_documents = count_documents + 1

for item in list_test:
    for s in sentences[item]:
        sentences_test.append(s)
    for l in labels[item]:
        labels_test.append(l)

if use_tfidf == 1:
    vectorizer = TfidfVectorizer(ngram_range=(1,max_ngrams), token_pattern=r'\b\w+\b', min_df=1)
else:
    vectorizer = CountVectorizer(ngram_range=(1,max_ngrams), token_pattern=r'\b\w+\b', min_df=1)

X_train = None
X_test = None

if embeddings_dir is not None:
    for item in list_train:
        with open(os.path.join(embeddings_dir,item)) as f:
            for line in f:
                A = np.fromstring(line[1:-1], sep=',')
                if X_train is None:
                    X_train = np.empty((0, A.shape[0]), float)
                X_train = np.vstack((X_train, A))
    for item in list_test:
        with open(os.path.join(embeddings_dir,item)) as f:
            for line in f:
                A = np.fromstring(line[1:-1], sep=',')
                if X_test is None:
                    X_test = np.empty((0, A.shape[0]), float)
                X_test = np.vstack((X_test, A))
else:
    X_train = vectorizer.fit_transform(sentences_train)
    X_test = vectorizer.transform(sentences_test)

y_train = labels_train
y_test = labels_test

parameters = {'C': np.power(2,np.arange(-10,10,dtype=float))}
svc = LinearSVC(class_weight='balanced')
gkf = list(GroupKFold(n_splits=5).split(X_train,y_train,documents_id_train))
clf = GridSearchCV(svc, parameters, scoring='f1_macro', cv=gkf, n_jobs=8)
clf = clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))
    print()

y_pred = clf.predict(X_test)
print(classification_report(y_test,y_pred))

np.savetxt(predictions_save_file,y_pred)
np.savetxt(labels_save_file,y_test)






