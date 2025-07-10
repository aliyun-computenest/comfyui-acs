#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始配置 Docker 凭证...${NC}"

# 创建 Docker 配置目录
mkdir -p ~/.docker

# 将 dockerconfigjson 解码并保存到 config.json
echo 'ewoJImF1dGhzIjogewoJCSJlZ3NsaW5nanVuLXJlZ2lzdHJ5LmNuLXd1bGFuY2hhYnUuY3IuYWxpeXVuY3MuY29tIjogewoJCQkiYXV0aCI6ICJiVzk1WVc5QU1Ua3dNekF4TlRBM05USXlPVEl3T1RwRGJuQkZVakEyTWxGdklRPT0iCgkJfQoJfQp9Cg==' | base64 -d > ~/.docker/config.json

# 检查配置文件是否正确创建
if [ -f ~/.docker/config.json ]; then
    echo -e "${GREEN}Docker 凭证配置成功!${NC}"
else
    echo "Docker 凭证配置失败，请检查错误信息"
    exit 1
fi

# 拉取 Docker 镜像
echo -e "${YELLOW}开始拉取 Docker 镜像...${NC}"
docker pull egslingjun-registry.cn-wulanchabu.cr.aliyuncs.com/egslingjun/inference-xpu-pytorch:25.05-v1.5.1-vllm0.8.5-torch2.6-cu126-20250528

# 创建并运行容器
echo -e "${YELLOW}创建并运行容器...${NC}"
CONTAINER_ID=$(docker run -d --gpus all -p 8188:8188 \
    egslingjun-registry.cn-wulanchabu.cr.aliyuncs.com/egslingjun/inference-xpu-pytorch:25.05-v1.5.1-vllm0.8.5-torch2.6-cu126-20250528 \
    sleep infinity)

echo -e "${GREEN}容器已创建，ID: ${CONTAINER_ID}${NC}"

# 在容器内执行命令
echo -e "${YELLOW}在容器内克隆 ComfyUI 仓库...${NC}"
docker exec $CONTAINER_ID bash -c "apt-get update && apt-get install -y git"
docker exec $CONTAINER_ID bash -c "git clone https://github.com/comfyanonymous/ComfyUI.git"

echo -e "${YELLOW}安装依赖...${NC}"
docker exec $CONTAINER_ID bash -c "cd ComfyUI && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"

# 在当前容器中直接启动 ComfyUI
echo -e "${YELLOW}在当前容器中启动 ComfyUI 服务器...${NC}"
docker exec -d $CONTAINER_ID bash -c "cd ComfyUI && python3 main.py --listen --port 8188 --fast"

# 为未来的容器准备启动脚本（仅用于新镜像）
echo -e "${YELLOW}为新镜像创建启动脚本...${NC}"
docker exec $CONTAINER_ID bash -c "echo '#!/bin/bash
cd /ComfyUI
python3 main.py --listen --port 8188 --fast' > /start_comfyui.sh"
docker exec $CONTAINER_ID bash -c "chmod +x /start_comfyui.sh"

# 提交为新镜像，并设置启动命令
echo -e "${YELLOW}将容器提交为新镜像 comfyui-wanx...${NC}"
docker commit --change='CMD ["/start_comfyui.sh"]' -a "User" -m "ComfyUI with Wan-X integration" $CONTAINER_ID comfyui-wanx:latest

# 确认镜像创建成功
echo -e "${GREEN}新镜像 comfyui-wanx 已创建!${NC}"
docker images | grep comfyui-wanx

echo -e "${GREEN}ComfyUI 服务器已在当前容器中启动!${NC}"
echo -e "${GREEN}可以通过 http://localhost:8188 访问${NC}"
echo -e "${GREEN}同时，你现在可以使用 comfyui-wanx:latest 镜像启动新的容器${NC}"

# 提供一些有用的命令
echo -e "${YELLOW}有用的命令:${NC}"
echo "查看当前容器日志: docker logs $CONTAINER_ID"
echo "进入当前容器: docker exec -it $CONTAINER_ID bash"
echo "停止当前容器: docker stop $CONTAINER_ID"
echo "使用新镜像启动新容器: docker run -d --gpus all -p 8188:8188 comfyui-wanx:latest"

# 保存容器 ID 到文件，方便后续操作
echo $CONTAINER_ID > comfyui_container_id.txt
echo -e "${GREEN}容器 ID 已保存到 comfyui_container_id.txt${NC}"
