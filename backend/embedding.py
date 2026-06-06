from sentence_transformers import SentenceTransformer

SENTENCETRANSFORMER=None
def get_model():
    global SENTENCETRANSFORMER
    if SENTENCETRANSFORMER is None:
        SENTENCETRANSFORMER=SentenceTransformer("all-MiniLM-L6-v2",device="mps")
    return SENTENCETRANSFORMER

def embedding(query:str)->list:
    model=get_model()
    vectors=model.encode(query,convert_to_tensor=True)
    return vectors.cpu().tolist()
