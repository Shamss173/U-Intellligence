import os
base = r"D:\Retrieval Augmented Generation\rag_system"
for item in os.listdir(base):
    full = os.path.join(base, item)
    if os.path.isdir(full):
        print(item)