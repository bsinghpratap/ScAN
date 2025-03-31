import spacy 
import re

class patientNoteParser: 
    def __init__(self, model="en_core_web_sm"): 
        self.nlp = spacy.load(model)
        self.nlp.max_length=1_500_000

    def extract_sentences(self, text):
        """Extract sentences along with their start and end indices."""
        doc = self.nlp(text)
        sentences = []
        for sent in doc.sents:
            clean_text = self._clean_sentence(sent.text)
            if clean_text:
                sentences.append({"text": clean_text,
                                  "start": sent.start_char,
                                  "end": sent.end_char})
        return sentences
    
    def _clean_sentence(self, sentence):
        """Remove excessive whitespace & special characters."""
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        sentence = re.sub(r'[^a-zA-Z0-9.,;!?\s]', '', sentence) # Remove special characters
        return sentence

    def group_into_paragraphs(self, sentences, num_sentences=20, overlap=5):
        """Groups sentences into paragraphs with overlap."""
        paragraphs = []
        for i in range(0, len(sentences), num_sentences - overlap):
            paragraph_sentences = sentences[i:i + num_sentences]
            # if not paragraph_sentences:
            #     break
            paragraph_text = ' '.join([s["text"] for s in paragraph_sentences])
            start_idx = paragraph_sentences[0]["start"]
            end_idx = paragraph_sentences[-1]["end"]
            paragraphs.append({
                "text": paragraph_text,
                "start": start_idx,
                "end": end_idx,
                "annotations": []
            })
        return paragraphs
    
    def add_annotations_to_paragraphs(self, paragraphs, annotations):
        """Assigns annotations to paragraphs based on overlapping start and end indices."""
        for key, annotation in annotations.items():
            start_ind, end_ind = int(annotation['annotation'][0]), int(annotation['annotation'][1])
            for paragraph in paragraphs:
                if end_ind >= paragraph["start"] and start_ind <= paragraph["end"]:
                    paragraph["annotations"].append(annotation)
        return paragraphs
