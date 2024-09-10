# Oracle 23ai workshop - 向量数据库

## Embedding模型部署（CPU）

考虑到硬件资源因素，没有足够的资源让每个人都部署一份模型，因此，本操作仅由讲师完成。讲师将向量嵌入模型部分为REST API 的方式，供大家调用。

### 环境安装

```shell
conda create -n ws23ai python=3.12

conda activate ws23ai

pip install -r requirements.txt
```

### 服务启动

先查看及编辑环境变量文件 app.env，确保文件中的设置正确，如数据库连接信息、模型路径等。再启动程序：

```pyt
python main.py
```

## LLM模型部署（GPU）

考虑到硬件资源因素，没有足够的资源让每个人都部署一份模型，因此，本操作仅由讲师完成。讲师将LLM模型部分为REST API 的方式，供大家调用。

#### 下载模型

从魔搭社区 (modelscope) 下载：[Qwen2-7B-Instruct](https://www.modelscope.cn/models/qwen/Qwen2-7B-Instruct)

#### 启动模型

我们采用vLLM来部署模型。vLLM是一个模型加速库，能大幅提升推理效率。

安装 vLLM：

```shell
conda create -n vllm python=3.12

conda activate vllm

pip install vllm

```

启动运行：

```shell
 python -m vllm.entrypoints.openai.api_server --port 8098 --model /home/ubuntu/ChatGPT/Models/Qwen/Qwen2-7B-Instruct  --served-model-name Qwen2-7B-Instruct --device=cuda --dtype auto --max-model-len=2048
```



#### Memo
```sql
grant create any directory to pocuser;

create directory RAG_DOC_DIR as '/u01/hysun/rag_docs';


create table RAG_FILES (
    file_name varchar2(500), 
    file_content BLOB
);


create table RAG_INDB_PIPELINE (
    id number, 
    name varchar2(50), 
    doc varchar2(500), 
    embedding VECTOR
);

Declare 
    mFile       VARCHAR2(500) := 'Oracle向量数据库_lab.pdf';
    mBLOB       BLOB := Empty_Blob();
    mBinFile    BFILE := BFILENAME('RAG_DOC_DIR', mFile);
Begin
    DBMS_LOB.OPEN(mBinFile, DBMS_LOB.LOB_READONLY);             -- Open BFILE
    DBMS_LOB.CreateTemporary(mBLOB, TRUE, DBMS_LOB.Session);    -- BLOB locator initialization
    DBMS_LOB.OPEN(mBLOB, DBMS_LOB.LOB_READWRITE);               -- Open BLOB locator for writing
    DBMS_LOB.LoadFromFile(mBLOB, mBinFile, DBMS_LOB.getLength(mBinFile));   -- Reading BFILE into BLOB
    DBMS_LOB.CLOSE(mBLOB);              -- Close BLOB locator
    DBMS_LOB.CLOSE(mBinFile);           -- Close BFILE
    
    INSERT INTO RAG_FILES(file_name, file_content) values (mFile, mBLOB);
    commit;
End;
/

insert into RAG_FILES(file_name, file_content) values('oracle-vector-lab', to_blob(bfilename('RAG_DOC_DIR', 'Oracle向量数据库_lab.pdf')));
commit;

select DBMS_LOB.getLength(FILE_CONTENT) from RAG_FILES;

drop table rag_doc_chunks purge;
create table rag_doc_chunks (doc_id varchar2(500), chunk_id number, chunk_data varchar2(4000), chunk_embedding vector);


-- utl_to_text: PDF -> TEXT
-- utl_to_chunks: TEXT -> CHUNKS
-- utl_to_embeddings: CHUNKS -> VECTORS
insert into rag_doc_chunks
select 
    dt.file_name doc_id, 
    et.embed_id chunk_id, 
    et.embed_data chunk_data, 
    to_vector(et.embed_vector) chunk_embedding
from
    rag_files dt,
    dbms_vector_chain.utl_to_embeddings(
        dbms_vector_chain.utl_to_chunks(
            dbms_vector_chain.utl_to_text(dt.file_content),
            json('{"normalize":"all"}')
        ),
        json('{"provider":"database", "model":"mydoc_model"}')
    ) t,
    JSON_TABLE(
        t.column_value, 
        '$[*]' COLUMNS (
            embed_id NUMBER PATH '$.embed_id', 
            embed_data VARCHAR2(4000) PATH '$.embed_data', 
            embed_vector CLOB PATH '$.embed_vector'
        )
    ) et;
commit;

insert into rag_doc_chunks
select 
    dt.file_name doc_id, 
    et.embed_id chunk_id, 
    et.embed_data chunk_data, 
    to_vector(et.embed_vector) chunk_embedding
from
    rag_files dt,
    dbms_vector_chain.utl_to_embeddings(
        dbms_vector_chain.utl_to_chunks(
            dbms_vector_chain.utl_to_text(dt.file_content),
            JSON('{ "by":"words",
           "max":"240",
           "overlap":"15",
           "split":"recursively",
           "language":"SIMPLIFIED CHINESE",
           "normalize":"all" }')
        ),
        json('{"provider":"database", "model":"mydoc_model"}')
    ) t,
    JSON_TABLE(
        t.column_value, 
        '$[*]' COLUMNS (
            embed_id NUMBER PATH '$.embed_id', 
            embed_data VARCHAR2(4000) PATH '$.embed_data', 
            embed_vector CLOB PATH '$.embed_vector'
        )
    ) et;
commit;


select 
    dbms_vector_chain.utl_to_chunks(TO_CLOB(FILE_CONTENT),
        JSON('{ "by":"words",
           "max":"240",
           "overlap":"15",
           "split":"recursively",
           "language":"SIMPLIFIED CHINESE",
           "normalize":"all" }'))
from RAG_FILES;



SELECT
    dbms_vector.utl_to_embedding(
        'This is a test',
        json('{
            "provider": "OCIGenAI",
            "credential_name": "OCI_GENAI_CRED_FOR_APEX",
            "url": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText",
            "model": "cohere.embed-multilingual-v3.0"
        }')
    ) embedding
FROM dual;

SELECT
    dbms_vector.utl_to_embedding(
        'This is a test',
        json('{
            "provider": "database",
            "model": "doc_model"
        }')
    ) embedding
FROM dual;

create or replace directory MODELS_DIR as '/u01/hysun/models';

EXEC DBMS_VECTOR.DROP_ONNX_MODEL(model_name => 'mydoc_model', force => true);

-- BEGIN
--     DBMS_VECTOR.LOAD_ONNX_MODEL(
--         directory => 'MODELS_DIR',
--         file_name => 'bge-base-zh-v1.5.onnx',
--         model_name => 'mydoc_model',
--         metadata   => JSON('{"function" : "embedding", "embeddingOutput" : "embedding", "input":{"input": ["DATA"]}}')
--     );
-- END;
-- /

BEGIN
    DBMS_VECTOR.LOAD_ONNX_MODEL(
        directory => 'MODELS_DIR',
        file_name => 'bge-base-zh-v1.5.onnx',
        model_name => 'mydoc_model'
    );
END;
/

SELECT vector_embedding(mydoc_model using 'hello' as data);


select 
    chunk_data，
    VECTOR_DISTANCE(chunk_embedding, VECTOR_EMBEDDING(mydoc_model USING '本次实验的先决条件' as data), COSINE) as distance
from rag_doc_chunks
order by distance
FETCH APPROX FIRST 1 ROWS ONLY;

BEGIN
    DBMS_VECTOR_CHAIN.CREATE_CREDENTIAL (
        CREDENTIAL_NAME  => 'LAB_OPENAI_CRED',
        PARAMS  => json('{ "access_token": "EMPTY" }')
    );
END;
/

select dbms_vector_chain.utl_to_generate_text(
 'Oracle 向量数据库是什么',
 json('{
    "provider": "openai",
    "credential_name": "LAB_OPENAI_CRED",
    "url": "http://146.235.226.110:8098/v1/chat/completions",
    "model": "Qwen2-7B-Instruct"
}') ) from dual;



select * 
from (
    select 
        chunk_data
    from rag_doc_chunks
    order by VECTOR_DISTANCE(chunk_embedding, VECTOR_EMBEDDING(mydoc_model USING '本次实验的先决条件' as data), COSINE)
    FETCH APPROX FIRST 3 ROWS ONLY
) dt,
dbms_vector_chain.utl_to_generate_text(
    dt.chunk_data,
    json('{
        "provider": "openai",
        "credential_name": "LAB_OPENAI_CRED",
        "url": "http://146.235.226.110:8098/v1/chat/completions",
        "model": "Qwen2-7B-Instruct"
    }') 
) rag


declare
    l_question varchar2(500) := '本次实验的先决条件';
    l_input CLOB;
    l_clob  CLOB;
    j apex_json.t_values;
    l_context   CLOB;
    l_rag_result CLOB;
begin  
    -- 第一步：从向量数据库中检索出与问题相似的内容
    for rec in (
        select 
        chunk_data
        from rag_doc_chunks
        order by VECTOR_DISTANCE(chunk_embedding, VECTOR_EMBEDDING(mydoc_model USING l_question as data), COSINE)
        FETCH APPROX FIRST 3 ROWS ONLY
    ) loop
        l_context := l_context || rec.chunk_data || chr(10);
    end loop;
  
    -- 第二步：提示工程：将相似内容和用户问题一起，组成大语言模型的输入
    l_input := '你是一个诚实且专业的数据库知识问答助手，请仅仅根据提供的上下文信息内容，回答用户的问题，且不要试图编造答案。\n 以下是上下文信息：' || replace(l_context, chr(10), '\n') || '\n请用英文回答用户问题：' || l_question;
    
  
    -- 第三步：调用大语言模型，生成RAG结果
    for rec in (select dbms_vector_chain.utl_to_generate_text(
        l_input,
        json('{
            "provider": "openai",
            "credential_name": "LAB_OPENAI_CRED",
            "url": "http://146.235.226.110:8098/v1/chat/completions",
            "model": "Qwen2-7B-Instruct"
        }') 
    ) as rag from dual) loop
        dbms_output.put_line('*** RAG Result: ' || rec.rag);
    end loop;
    -- apex_json.parse(j, l_clob); 
    -- l_rag_result := apex_json.get_varchar2(p_path => 'choices[%d].message.content', p0 => 1, p_values => j);
  
    -- dbms_output.put_line('*** RAG Result: ' || l_rag_result);
end;
/

```