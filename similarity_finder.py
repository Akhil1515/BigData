import spacy

nlp = spacy.load('en_core_web_lg')


def get_similarity_using_spacy(sentence1, sentence2):
    similarity_score = abs(get_dependency_parsing(sentence1).similarity(get_dependency_parsing(sentence2)))
    return similarity_score


def get_dependency_parsing(sentence):
    dependency_parsed_sentence = nlp(sentence)
    return dependency_parsed_sentence


if __name__ == '__main__':
    option = "yes"
    while "yes" == option:
        sentence1 = input('Enter 1st sentence ')
        sentence2 = input('Enter 2nd sentence ')
        similarity_score = get_similarity_using_spacy(sentence1, sentence2)
        print(similarity_score)
        option = input('Do you want to continue')