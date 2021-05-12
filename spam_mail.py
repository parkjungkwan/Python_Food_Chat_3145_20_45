from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import names
from nltk.stem import WordNetLemmatizer
import glob
import os
import numpy as np
ham = './ham/0007.1999-12-14.farmer.ham.txt'
spam = './spam/0058.2003-12-21.GP.spam.txt'
with open(ham, 'r') as infile:
    ham_sample = infile.read()
print(ham_sample)
print('-----------------------')
with open(spam, 'r') as infile:
    spam_sample = infile.read()
print(spam_sample)
cv = CountVectorizer(stop_words="english", max_features=500)
emails, labels = [], []
file_path = './ham/'
for filename in glob.glob(os.path.join(file_path, '*.txt')):
    with open(filename, 'r', encoding= 'ISO-8859-1') as infile:
        emails.append(infile.read())
        labels.append(0)
file_path = './spam/'
for filename in glob.glob(os.path.join(file_path, '*.txt')):
    with open(filename, 'r', encoding= 'ISO-8859-1') as infile:
        emails.append(infile.read())
        labels.append(1)
def letters_only(astr):
    return astr.isalpha()
import nltk
# nltk.download('all') # 영어사전 다운로드
all_names = set(names.words())
lemmatizer = WordNetLemmatizer()
def clean_text(docs):
    cleaned_docs = []
    for doc in docs:
        cleaned_docs.append(' '.join([lemmatizer.lemmatize(word.lower())
                                        for word in doc.split()
                                        if letters_only(word)
                                        and word not in all_names]))
    return cleaned_docs
cleaned_emails = clean_text(emails)
term_docs = cv.fit_transform(cleaned_emails)
print(term_docs[0])
feature_mapping = cv.vocabulary
feature_names = cv.get_feature_names()
def get_label_index(labels):
    from collections import defaultdict
    label_index = defaultdict(list)
    for index, label in enumerate(labels):
        label_index[label].append(index)
    return label_index
def get_prior(label_index):
    prior = {label: len(index) for label, index in label_index.items()}
    total_count = sum(prior.values())
    for label in prior:
        prior[label] /= float(total_count)
    return prior


def get_likelihood(term_document_matrix, label_index, smoothing=0):
    # ------아규먼트의 의미--------
    # term_document_matrix :  행렬구조로 된 문자
    # label_index : 그룹핑된 레이블의 인덱스
    # smoothing
    # --------------
    likelihood = {}
    for label, index in label_index.items():
        likelihood[label] = term_document_matrix[index, :].sum(axis=0) + smoothing
        likelihood[label] = np.asarray(likelihood[label])[0]
        total_count = likelihood[label].sum()
        likelihood[label] = likelihood[label] / float(total_count)
    return likelihood
feature_names[:5]
def get_posterior(term_document_matrix, prior, likelihood):
    num_docs = term_document_matrix.shape[0]
    posteriors = []
    for i in range(num_docs):
        posterior = {key: np.log(prior_label) \
                     for key, prior_label in prior.items()}
        for label, likelihood_label in likelihood.items():
            term_document_vector = term_document_matrix.getrow(i)
            counts = term_document_vector.data
            indices = term_document_vector.indices
            for count, index in zip(counts, indices):
                posterior[label] += np.log(likelihood_label[index]) * count
        min_log_posterior = min(posterior.values())
        for label in posterior:
            try:
                posterior[label] = np.exp(posterior[label] - min_log_posterior)
            except:
                posterior[label] = float('inf')
        sum_posterior = sum(posterior.values())
        for label in posterior:
            if posterior[label] == float('inf'):
                posterior[label] = 1.0
            else:
                posterior[label] /= sum_posterior
        posteriors.append(posterior.copy())
    return posteriors
label_index = get_label_index(labels)
prior = get_prior(label_index)
smoothing = 1
likelihood = get_likelihood(term_docs, label_index, smoothing)
emails_test = [
   '''Subject: flat screens
   hello ,
   please call or contact regarding the other flat screens requested .
   trisha tlapek - eb 3132 b
   michael sergeev - eb 3132 a
   also the sun blocker that was taken away from eb 3131 a .
   trisha should two monitors also michael .
   thanks
   kevin moore''',
   '''Subject: having problems in bed ? we can help !
   cialis allows men to enjoy a fully normal sex life without having to plan the sexual act .
   if we let things terrify us , life will not be worth living .
   brevity is the soul of lingerie .
   suspicion always haunts the guilty mind .''',
]
cleaned_test = clean_text(emails_test)
term_docs_test = cv.transform(cleaned_test)
posterior = get_posterior(term_docs_test, prior, likelihood)
print(posterior)