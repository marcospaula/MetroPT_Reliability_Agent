# kb/ — document base for RAG

The same idea as the boiler repository's "RAG docs", with one difference in honesty:
there the documents were written by the author and read like real plant documents.

Here every document we write carries a header stating that it is **synthetic**, along
with the technical source it rests on. A plant document that does not exist must not
look as though it does.

Eight notes, searched by the `kb_search` MCP tool with a BM25-ish ranking over
sections. No embeddings and no vector store: at this size they would add dependencies
without adding recall.

| | |
|---|---|
| `datasheets/` | compressor, air dryer and drains, reservoirs and clients |
| `controls/` | the load and unload cycle, and why it is the diagnostic |
| `troubleshooting/` | the air-leak signature, and reading the LPS floor |
| `maintenance/` | the 2020 reports with their defects, and the data-quality traps |

Every note carries `synthetic: true`, the sources it rests on, and a header saying it
is a derived note rather than a plant document. Statements quoted from a source and
statements measured by this repository are distinguished in the text.
