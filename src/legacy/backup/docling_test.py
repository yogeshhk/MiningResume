from docling.document_converter import DocumentConverter

source = "data/YogeshKulkarniLinkedInProfile.pdf"  # local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"
