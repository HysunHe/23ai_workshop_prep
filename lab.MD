建表：

CREATE TABLE <表名> (
    id VARCHAR2(50) DEFAULT SYS_GUID() PRIMARY KEY,
    dataset_name VARCHAR2(50) NOT NULL,
    document CLOB,
    cmetadata JSON,
    embedding VECTOR
);

select * from lab_vecstore;

select to_char(cmetadata), json_value(cmetadata, '$.source') from lab_vecstore;

初始化数据：

curl -X 'POST' \
  'http://localhost:18000/workshop/prepare-data' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "table_name": "<表名>",
  "dataset_name": "oracledb_docs"
}'


curl -X 'POST' \
  'http://localhost:18000/workshop/embedding' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '"Oracle 23ai 新特性"'