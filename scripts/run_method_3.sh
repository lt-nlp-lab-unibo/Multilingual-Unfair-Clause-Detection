corpus=$1

ngrams=2
tfidf=0

for translation in google opus joshua
do

for lang in de it pl
do

resdir="experiments_method_3_$translation/$lang/"
test -d $resdir || mkdirhier $resdir

for fold in 0 1 2 3 4
do

python3 scripts/linear_svm_transl.py $corpus/sentences/$lang/translated_from_en_"$translation" $corpus/sentences/$lang/original $corpus/tags/en/original $corpus/tags/$lang/original $corpus/list_tags.txt $corpus/lists/LIST_TRAIN_$fold.txt $corpus/lists/LIST_TEST_$fold.txt $ngrams $tfidf $resdir/y_pred_$fold.txt $resdir/y_true_$fold.txt > $resdir/log_$fold.txt

done

done

done

