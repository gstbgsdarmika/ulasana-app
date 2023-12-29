# import pickle
import numpy as np

def predict_sentiment():
    # Define classification pipelines for each model
    model_tfidf_SVM = pickle.load(open('./model/machine/svm_tfidf_model.pkl', 'rb'))
    
    with open('./model/machine/best_tfidf_vocabulary_SVM.pkl', 'rb') as f:
        best_vocabulary_SVM = pickle.load(f)
    
    # Create a new TfidfVectorizer with the loaded vocabulary
    tfidf_vectorizer_svm = TfidfVectorizer(vocabulary=best_vocabulary_SVM)  # You can adjust the max_features parameter
    X_TFIDF_SVM = tfidf_vectorizer_svm.fit_transform(df_preprocessed2["preprocessed"]).toarray()

    result = model_tfidf_SVM.score(X_TFIDF_SVM, y)
    print('accuracy: ', result)