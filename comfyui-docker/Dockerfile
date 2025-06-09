# 使用原始镜像作为基础
FROM egslingjun-registry.cn-wulanchabu.cr.aliyuncs.com/egslingjun/inference-xpu-pytorch:25.05-v1.5.1-vllm0.8.5-torch2.6-cu126-20250528

# 设置工作目录
WORKDIR /workspace/pytorch

# 安装系统依赖（git、ffmpeg 等）
RUN apt-get update && \
    apt-get install -y git ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制并执行自定义节点安装脚本
COPY download_custom_nodes_script.sh /tmp/
RUN chmod +x /tmp/download_custom_nodes_script.sh && \
    cd /root && \
    /tmp/download_custom_nodes_script.sh
RUN pip install --no-cache-dir \
    opencv-python-headless \
    scikit-learn \
    matplotlib \
    pandas \
    numba \
    xformers \
    SageAttention
WORKDIR /workspace/pytorch/ComfyUI

# 暴露端口
EXPOSE 8188

# 设置默认命令
CMD ["python3", "main.py", "--listen", "--port", "8188", "--fast"]
