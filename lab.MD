建表：

CREATE TABLE lab_vecstore (
    id VARCHAR2(50) DEFAULT SYS_GUID() PRIMARY KEY,
    dataset_name VARCHAR2(50) NOT NULL,
    document CLOB,
    cmetadata JSON,
    embedding VECTOR
);

select * from lab_vecstore;

select to_char(cmetadata), json_value(cmetadata, '$.source') from lab_vecstore;
