class DocumentProcessing:
    def __init__(self):
        self.text = ""
       
    def read_document(self, file):
        """
        Read the document from the provided file path.
        """
        with open(file, 'r', encoding='utf-8') as f:
            self.text = f.read()
        return self.text