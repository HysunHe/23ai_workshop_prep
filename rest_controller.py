""" 
Description: 
 - Workshop demo application.

History:
 - 2024/08/27 by Hysun (hysun.he@oracle.com): Initial version
"""

import os
import oracledb
import load_utils
from oracledb import Connection
from langchain_huggingface import HuggingFaceEmbeddings
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from langchain.docstore.document import Document
from JsonResponse import Response

from dotenv import load_dotenv
load_dotenv("app.env")

# 数据库连接信息
username = os.environ.get("DB_USER")
password = os.environ.get("DB_PWD")
dsn = os.environ.get("DB_DSN")
# print(f"{username} - {password} - {dsn}")

# 加载 Embeddings 模型
embedding_model = HuggingFaceEmbeddings(
    model_name=os.environ.get("EMBEDDING_MODEL"),
    model_kwargs={"device": "cpu"},
)

_app = FastAPI(
    openapi_url=f"{os.environ.get("CONTEXT_ROOT")}/openapi.json",
    docs_url=f"{os.environ.get("CONTEXT_ROOT")}/docs",
)

_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embeddings_cache = dict()

def app() -> FastAPI:
    return _app

def init():
    print("# Init data...")
    documents = load_utils.load_files(os.environ.get("DATA_SET_PATH"))
    for doc in documents:
        doc_name = doc.metadata["source"]
        if doc_name in embeddings_cache:
            continue
        embedding = embedding_model.embed_documents([doc.page_content])[0]
        embeddings_cache[doc_name] = embedding
        print(f"# Vectorized {doc_name}")
    print("# Init data...[OK]")
        
        
def insert_one_document(client: Connection, table_name: str, dataset_name: str, doc: Document):
    """ 对一个 Document 进行向量化并插入到数据库中。这是在 Demo 环境下为避免资源紧张采取的做法。实际应用中，
        可以采用批量向量化以及 cursor.executemany(...) 进行批量插入。
    """
    
    print(f"# Processing {doc.metadata}")
    doc_name = doc.metadata["source"]
    if doc_name in embeddings_cache:
        embedding = embeddings_cache.get(doc_name)
    else:
        embedding = embedding_model.embed_documents([doc.page_content])[0]
        embeddings_cache[doc_name] = embedding
        
    # metadata = json.dumps(doc.metadata, ensure_ascii=False)
    data = (dataset_name, embedding, doc.page_content, doc.metadata)
    affected_rows = 0
    with client.cursor() as cursor:
        cursor.setinputsizes(
            oracledb.DB_TYPE_VARCHAR, oracledb.DB_TYPE_VECTOR, oracledb.DB_TYPE_CLOB, oracledb.DB_TYPE_JSON
        )
        # 实际应用中，可以采用 cursor.executemany(...) 进行批量插入
        cursor.execute(
            f"INSERT INTO {table_name} (dataset_name, embedding, document, cmetadata) VALUES (:1, to_vector(:2), :3, :4)",
            data,
        )
        affected_rows = cursor.rowcount
        client.commit()
    return affected_rows


@_app.post(f"{os.environ.get("CONTEXT_ROOT")}/prepare-data")
def prepare_data(
    table_name: str = Body(examples=["lab_vecstore_<your_name>", "lab_vecstore_david"]),
    dataset_name: str = Body(examples=["oracledb_docs", "mylab_test_data"]),
) -> Response:
    print(f"# Got prepare_data request: {table_name} - {dataset_name}")

    # 加载数据集
    documents = load_utils.load_files(os.environ.get("DATA_SET_PATH"))
    print(f"### Dataset size(rows): {len(documents)}")
    
    # 数据入库
    print("# Inserting data to the vector store...")
    row_inserted = 0
    with oracledb.connect(user=username, password=password, dsn=dsn) as connection:
        for docu in documents:
            c = insert_one_document(client=connection, table_name=table_name, dataset_name=dataset_name,doc=docu)
            row_inserted = row_inserted + c
    
    resp: Response = Response(status="OK", message=f"Operation succeeded. Affected rows: {row_inserted} (for table {table_name})", data={})
    print(f"# {vars(resp)}")
    
    return resp


@_app.post(f"{os.environ.get("CONTEXT_ROOT")}/embedding")
def embedding_query(
    query: str = Body(examples=["Oracle 23ai 新特性", "Oracle向量数据库是什么"])
) -> Response:
    print(f"# Got embedding_query request: {query}")

    embedding = embedding_model.embed_query(text=query)
    
    resp: Response = Response(status="OK", message=f"Operation succeeded.", data={"embedding": embedding})
    print(f"# {vars(resp)}")
    
    return resp

