# Oracle 23ai workshop - 向量数据库

## Embedding模型部署（CPU)

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
