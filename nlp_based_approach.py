# -*- coding: utf-8 -*-
"""NLP based approach.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ywkfqP8yZX08-oOFWRM067BmJSBZeD2V
"""

!pip install stanza

import stanza

# Initialize the Stanza NLP pipeline for Tamil language
stanza.download('ta')  # Download the Tamil model
nlp = stanza.Pipeline('ta')  # Create the NLP pipeline for Tamil

# Function to identify and correct subject-verb agreement errors
def check_subject_verb_agreement(sentence):
    corrected_sentence = sentence
    doc = nlp(sentence)

    for sent in doc.sentences:
        subject = None
        verb = None

        # Check for subject-verb pairs
        for word in sent.words:
            if word.deprel == 'nsubj':  # If the word is a subject
                subject = word.text
            elif word.deprel == 'root':  # If the word is the main verb
                verb = word.text

        # Check for subject-verb agreement (singular/plural mismatch)
        if subject and verb:
            # If subject is singular but verb is plural or vice versa, correct it
            if subject.endswith('்கள்') and verb.endswith('கிறது'):
                corrected_sentence = sentence.replace(verb, verb[:-3] + 'நர்கள்')  # Change "கிறது" to "நர்கள்"
            elif not subject.endswith('்கள்') and verb.endswith('கின்றனர்'):
                corrected_sentence = sentence.replace(verb, verb[:-3] + 'கின்றார்')  # Change "கின்றனர்" to "கின்றார்"

    return corrected_sentence

# Function to detect and correct tense errors
def check_tense_errors(sentence):
    corrected_sentence = sentence
    doc = nlp(sentence)

    # Check if the verb tenses are consistent
    for sent in doc.sentences:
        for word in sent.words:
            if word.upos == 'VERB':
                verb = word.text
                if 'போதினான்' in verb:  # Example: Past tense
                    corrected_sentence = sentence.replace(verb, 'போகின்றான்')  # Change past tense to present if necessary
    return corrected_sentence

# Function to process and correct grammar errors
def correct_grammar(text):
    # First, correct subject-verb agreement errors
    corrected_text = check_subject_verb_agreement(text)
    # Then, correct tense errors
    corrected_text = check_tense_errors(corrected_text)

    return corrected_text

# Input Tamil paragraph (for testing)
input_paragraph = "அவர்கள் கற்றுக்கொள்கின்றார். நான் பயணிக்கின்றேன். ஆனால், உயிர்கள் வேகமாக ஓடுகிறது."

# Process and correct the paragraph
corrected_paragraph = correct_grammar(input_paragraph)

# Output the corrected paragraph
print("Input Paragraph:")
print(input_paragraph)
print("\nCorrected Paragraph:")
print(corrected_paragraph)