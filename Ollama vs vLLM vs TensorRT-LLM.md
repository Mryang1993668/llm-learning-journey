🚀 大模型推理引擎三剑客：Ollama vs vLLM vs TensorRT-LLM
面向开发人员的实战指南
理解它们是什么、有什么价值、怎么用，以及如何根据场景选型

📝 写在前面
作为大模型开发人员，你一定会遇到这三个工具：Ollama、vLLM、TensorRT-LLM。它们都是用来“跑模型”的，但定位完全不同：

Ollama：个人开发者的“瑞士军刀”

vLLM：团队服务的“高性能引擎”

TensorRT-LLM：企业生产的“性能怪兽”

本文从开发人员视角出发，帮你搞清楚：

它们分别是什么（核心定位）

它们能帮你解决什么问题（核心价值）

你怎么上手使用（开发实践）

什么场景该选哪个（选型指南）

一、Ollama：个人开发者的“模型管家”

1.1 它是什么？
Ollama 是一个开源的本地大模型运行工具，专为个人开发者设计，让你能像使用命令行工具一样轻松跑模型。

本质：把模型打包成“一行命令就能跑”的简化工具

核心哲学：“简单到极致”——下载、运行、聊天，三步搞定

底层：基于 llama.cpp，主力支持 GGUF 格式

1.2 核心价值
| 价值点 | 说明 | 对开发者的意义 |
|--------|------|---------------|
| 零配置上手 | 安装完就能用，不用配环境、不用写代码 | 5 分钟从零到第一个对话 |
| 模型市场 | ollama pull 直接下载热门模型 | 不用去 Hugging Face 翻找 |
| API 服务 | 默认开启 localhost:11434，提供 REST API | 可快速集成到自己的应用 |
| 跨平台 | Windows、macOS、Linux 全支持 | 开发环境统一 |
| Modelfile | 可自定义模型参数、系统提示词 | 像写 Dockerfile 一样定制模型 |

1.3 开发人员怎么用？
🛠️ 安装

macOS
brew install ollama

Linux
curl -fsSL https://ollama.com/install.sh | sh

Windows
下载 .msi 安装包，双击安装

🛠️ 日常使用

下载模型
ollama pull deepseek-r1:7b

直接对话
ollama run deepseek-r1:7b

启动 API 服务（供其他程序调用）
ollama serve

🛠️ 集成到 Python 应用

python

import requests

import json

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "deepseek-r1:7b",
        "prompt": "公司有什么福利？",
        "stream": False
    }
)

print(response.json()["response"])

🛠️ 自定义模型（Modelfile）

dockerfile

Modelfile

FROM deepseek-r1:7b

PARAMETER temperature 0.7

SYSTEM """你是一个专业的HR助手，请简洁回答公司政策相关问题。"""

ollama create hr-assistant -f Modelfile

ollama run hr-assistant


1.4 适合场景
✅ 适合场景

个人学习、本地调试

快速验证模型效果

集成到个人项目

团队内部小范围分享

二、vLLM：团队服务的“高性能引擎”

2.1 它是什么？
vLLM 是一个专为“高并发、大规模”场景设计的 LLM 推理和服务引擎，由 UC Berkeley 开发，现已成为工业界事实标准。

本质：把模型推理做成了“工业级服务”

核心创新：PagedAttention（分页注意力），把内存利用率从 30% 提升到 90%+

定位：介于 Ollama（个人）和 TensorRT-LLM（专业卡）之间的通用高性能方案

2.2 核心价值
| 价值点 | 说明 | 对开发者的意义 |
|--------|------|---------------|
| 吞吐量王者 | 持续批处理 + PagedAttention，吞吐量提升最高 23 倍 | 同样的硬件，服务更多用户 |
| OpenAI 兼容 API | 启动后直接提供和 OpenAI 一模一样的接口 | 已有代码零成本迁移 |
| 生产级特性 | 流式输出、多 GPU 并行、量化支持、前缀缓存 | 企业需要的能力它都有 |
| 生态地位 | Thoughtworks 技术雷达“采纳”级别，Azure 默认引擎 | 社区活跃，问题好解决 |
| 硬件友好 | 支持消费卡和专业卡，不需要特定硬件 | 开发和生产环境可以一致 |

2.3 开发人员怎么用？

🛠️ 安装

pip install vllm

🛠️ 离线推理（像用普通库）

python

from vllm import LLM, SamplingParams

加载模型（自动从 Hugging Face 下载）
llm = LLM(model="Qwen/Qwen2.5-7B-Instruct")

批量处理
prompts = ["公司有什么福利？", "请假怎么请？"]
sampling_params = SamplingParams(temperature=0.1, max_tokens=512)

outputs = llm.generate(prompts, sampling_params)
for output in outputs:
    print(output.outputs[0].text)

🛠️ 启动 API 服务（核心用法）

一行命令启动 OpenAI 兼容服务

vllm serve Qwen/Qwen2.5-7B-Instruct \
  --port 8000 \
  --tensor-parallel-size 2  # 用 2 张 GPU

🛠️ 从应用调用（和 OpenAI SDK 完全兼容）

from openai import OpenAI

只需要改 base_url
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[{"role": "user", "content": "公司有什么福利？"}]
)
print(response.choices[0].message.content)

🛠️ 容器化部署
dockerfile
FROM vllm/vllm-openai:latest
CMD ["vllm", "serve", "Qwen/Qwen2.5-7B-Instruct", "--port", "8000"]

docker run --gpus all -p 8000:8000 vllm-image

2.4 适合场景
✅ 适合场景

团队内部 API 服务

几十到几百并发

消费卡和专业卡混用

快速上线 MVP 产品

需要 OpenAI 兼容接口

三、TensorRT-LLM：企业生产的“性能怪兽”

3.1 它是什么？
TensorRT-LLM 是 NVIDIA 专门为自家 GPU 打造的“核武器级”推理引擎，能把大模型在 A100/H100 等专业显卡上压榨出极限性能。

本质：不是简单的“加载模型”，而是把模型“编译”成针对具体 GPU 的“引擎文件”

核心哲学：“一次编译，极致运行”

定位：NVIDIA 专业卡的“专属性能解锁器”

3.2 核心价值
| 价值点 | 说明 | 对开发者的意义 |
|--------|------|---------------|
| 极致性能 | GPU 利用率 95%+，吞吐量比 PyTorch 高 8 倍 | 同样的硬件，服务更多用户 |
| 成本控制 | 70B 模型从 4 张卡减到 1 张卡（INT4 量化） | 硬件成本直降 75% |
| 企业级特性 | 多卡并行、多机多卡、FP8 支持、Triton 集成 | 生产环境需要的它都有 |
| NVIDIA 亲儿子 | 官方维护，第一时间支持新硬件和新特性 | 未来兼容性有保障 |
| 量化全家桶 | FP16/BF16/INT8/INT4/FP8 全支持 | 可以在精度和速度间自由权衡 |

3.3 开发人员怎么用？

🛠️ 核心概念：引擎（Engine）
TensorRT-LLM 的使用流程和 vLLM 完全不同——vLLM 是“加载即用”，TensorRT-LLM 是“编译后用”。
````
text
[Hugging Face 模型] 
    ↓ (编译、优化)
[TensorRT 引擎文件] ← 针对具体 GPU（如 A100）生成
    ↓ (加载运行)
[极致推理性能]
关键：引擎文件是硬件绑定的——为 A100 编译的引擎，不能在 V100 上跑。
````

🛠️ 环境准备（容器化是官方最佳实践）

拉取 NVIDIA 官方 TensorRT-LLM 容器
docker run --gpus all -it --rm \
  -v $(pwd):/workspace \
  nvcr.io/nvidia/tensorrt-llm/release:latest

🛠️ 下载模型

huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir ./qwen-model

🛠️ 编译成引擎（核心步骤）

trtllm-build \
  --model_dir ./qwen-model \
  --dtype float16 \
  --max_batch_size 8 \
  --max_input_len 2048 \
  --max_output_len 512 \
  --output_dir ./qwen-engine

🛠️ 运行推理

import tensorrt_llm
from tensorrt_llm.runtime import ModelRunner

加载编译好的引擎
runner = ModelRunner.from_dir(
    engine_dir="./qwen-engine",
    rank=0
)

生成回答
output = runner.generate(
    ["公司有什么福利？"],
    max_new_tokens=256,
    temperature=0.1
)
print(output[0])

🛠️ 部署成服务（配合 Triton）

准备模型仓库
mkdir -p model_repo/qwen/1
cp -r ./qwen-engine/* model_repo/qwen/1/

启动 Triton 服务
tritonserver --model-repository=./model_repo

3.4 适合场景
✅ 适合场景

A100/H100 等专业卡

几百人以上的高并发

成本敏感的生产环境

需要 FP8 等新特性

大厂、云服务商

四、三剑客终极对比（开发人员视角）

4.1 核心特性对比表
| 对比维度 | Ollama | vLLM | TensorRT-LLM |
|---------|--------|------|--------------|
| **一句话定位** | 个人模型管家 | 通用高性能引擎 | NVIDIA 专属性能怪兽 |
| **核心哲学** | 简单到极致 | 吞吐量优先 | 编译优化、榨干硬件 |
| **使用方式** | 命令行 + REST API | Python API + HTTP | 编译引擎 + Runtime API |
| **上手难度** | ⭐ 极低 | ⭐⭐ 中等 | ⭐⭐⭐ 高（需编译） |
| **硬件要求** | 任何 GPU/CPU | 任何 GPU | **NVIDIA 专业卡优先** |
| **多卡并行** | 不支持 | 有限支持 | **全支持（TP/PP/EP）** |
| **多机部署** | 不支持 | 不支持 | **支持（NCCL + Triton）** |
| **量化支持** | GGUF | GPTQ/AWQ | **INT4/INT8/FP8/BF16 全家桶** |
| **API 格式** | 自定义 | OpenAI 兼容 | Triton 协议 |
| **并发能力** | 低（单用户） | 高（数百并发） | **极高（数千并发）** |
| **内存效率** | 普通 | **PagedAttention 革命性提升** | 也有 PagedAttention |
| **GPU 利用率** | 60-70% | 80-90% | **95%+** |

4.2 开发体验对比表
| 开发维度 | Ollama | vLLM | TensorRT-LLM |
|---------|--------|------|--------------|
| **从下载到运行** | 3 分钟 | 10 分钟 | 1 小时（含编译） |
| **代码量** | 3 行 | 10 行 | 30 行 |
| **调试难度** | 极低 | 中等 | 高 |
| **模型切换** | `ollama run 新模型` | 重启服务 | 重新编译 |
| **版本迭代** | 快 | 中 | 慢（需要重新编译） |
| **社区支持** | 活跃 | **非常活跃** | 企业级支持 |

4.3 硬件成本对比表（以 70B 模型为例）
| 精度 | 显存需求 | Ollama | vLLM | TensorRT-LLM |
|------|---------|--------|------|--------------|
| **FP16** | 140GB | ❌ 不支持 | ✅ 4 张 A100 | ✅ 4 张 A100 |
| **INT8** | 98GB | ❌ 不支持 | ✅ 2 张 A100 | ✅ 2 张 A100 |
| **INT4** | **56GB** | ✅ GGUF Q4 | ✅ GPTQ 4bit | ✅ **1 张 A100** |
关键结论：当模型规模大、成本敏感时，TensorRT-LLM 的优势才真正体现出来。

五、开发人员选型指南
5.1 从你的硬件出发
| 你的硬件 | 首选 | 备选 | 理由 |
|---------|------|------|------|
| 8GB 消费卡 | **Ollama** | LM Studio | 只能跑小模型量化版，Ollama 最简单 |
| 24GB 消费卡 | **vLLM** | Ollama | 能跑 7B-13B，vLLM 可做服务 |
| A100/H100 | **TensorRT-LLM** | vLLM | 不选 TensorRT-LLM 亏了硬件 |
| MacBook | **Ollama** | - | Metal 加速支持好 |

5.2 从你的场景出发
| 场景 | 推荐 | 理由 |
|------|------|------|
| 个人学习、本地调试 | Ollama | 最简单，不用折腾 |
| 快速验证模型效果 | Ollama | 换模型最快 |
| 团队内部 API 服务 | vLLM | 吞吐量高，OpenAI 兼容 |
| 几十人并发 | vLLM | 性价比最高 |
| 几百人以上并发 | TensorRT-LLM | 硬件利用率最关键 |
| 成本敏感的生产环境 | TensorRT-LLM | 用更少的卡跑更多的请求 |
| 需要 FP8 等新特性 | TensorRT-LLM | 只有它支持 |
| 多机多卡分布式 | TensorRT-LLM | 唯一选择 |

5.3 你的学习路径建议

[Ollama] → 个人学习、本地调试（已掌握）
    ↓
[vLLM] → 团队服务、几十并发（可以开始学）
    ↓
[TensorRT-LLM] → 企业生产、极致性能（有需要再学）

六、总结：一句话记住它们
| 工具 | 一句话记住 |
|------|-----------|
| **Ollama** | 个人开发者的“模型管家”——简单到极致，一行命令跑模型 |
| **vLLM** | 团队服务的“高性能引擎”——PagedAttention 革命，OpenAI 兼容 |
| **TensorRT-LLM** | 企业生产的“性能怪兽”——编译优化，把 A100 榨干 |

📌 附：常用命令速查表

Ollama

ollama pull deepseek-r1:7b
ollama run deepseek-r1:7b
ollama serve

vLLM

vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000

TensorRT-LLM

编译
trtllm-build --model_dir ./model --output_dir ./engine

运行
python -c "from tensorrt_llm.runtime import ModelRunner; runner = ModelRunner.from_dir('./engine'); print(runner.generate(['prompt']))"
最后的话：这三个工具不是“哪个更好”的关系，而是不同阶段、不同场景下的最佳选择。从 Ollama 入门，用 vLLM 做服务，等真正需要榨干硬件时再上 TensorRT-LLM——这才是大模型开发人员的理性进阶路径。