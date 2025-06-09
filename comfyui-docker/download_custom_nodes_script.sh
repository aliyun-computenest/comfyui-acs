#!/bin/bash

set -euo pipefail

function clone_and_install () {
    local original_dir=$(pwd)
    local url="$1"
    local repo_name=$(basename "$url" .git)

    # 克隆阶段
    echo "🔻 开始克隆: $repo_name"
    if ! git clone --depth=1 --no-tags --recurse-submodules --shallow-submodules "$url"; then
        echo "❌ 克隆失败: $url" >&2
        return 1
    fi

    # 安装依赖阶段
    echo "📂 进入目录: $repo_name"
    cd "$repo_name" || return 2
    if [[ -f requirements.txt ]]; then
        echo "🔧 安装依赖: $repo_name"
        pip install -r requirements.txt > /dev/null
    else
        echo "ⓘ 未找到 requirements.txt"
    fi

    # 返回原目录
    echo "↩️ 返回上级目录"
    cd "$original_dir"

    # 返回完整路径
    echo "$(pwd)/$repo_name"
    echo "✅ 完成处理: $repo_name"
    echo "----------------------------------"
}

function clone () {
      set +e ;
      git clone --depth=1 --no-tags --recurse-submodules --shallow-submodules "$1";
      set -e ;
}


cd /workspace/pytorch
clone https://github.com/comfyanonymous/ComfyUI.git
cd /workspace/pytorch/ComfyUI
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cd /workspace/pytorch/ComfyUI/custom_nodes
clone_and_install https://github.com/ltdrdata/ComfyUI-Manager.git
clone_and_install https://github.com/kijai/ComfyUI-WanVideoWrapper.git
clone_and_install https://github.com/crystian/ComfyUI-Crystools.git
clone_and_install https://github.com/crystian/ComfyUI-Crystools-save.git
clone_and_install https://github.com/Wan-Video/Wan2.1.git
clone_and_install https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git
clone_and_install https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
clone_and_install https://github.com/welltop-cn/ComfyUI-TeaCache.git
clone_and_install https://github.com/sh570655308/ComfyUI-TopazVideoAI.git
# General
clone_and_install https://github.com/cubiq/ComfyUI_InstantID.git
clone_and_install https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git
clone_and_install https://github.com/bash-j/mikey_nodes.git
clone_and_install https://github.com/kijai/ComfyUI-GIMM-VFI.git

clone https://github.com/chrisgoringe/cg-use-everywhere.git
clone https://github.com/cubiq/ComfyUI_essentials.git
clone https://github.com/jags111/efficiency-nodes-comfyui.git
clone https://github.com/kijai/ComfyUI-KJNodes.git
clone https://github.com/rgthree/rgthree-comfy.git
clone https://github.com/shiimizu/ComfyUI_smZNodes.git
clone https://github.com/WASasquatch/was-node-suite-comfyui.git

clone https://github.com/cubiq/PuLID_ComfyUI.git
clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
clone https://github.com/florestefano1975/comfyui-portrait-master.git
clone https://github.com/Gourieff/ComfyUI-ReActor.git
clone https://github.com/huchenlei/ComfyUI-layerdiffuse.git
clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git
clone https://github.com/mcmonkeyprojects/sd-dynamic-thresholding.git
clone https://github.com/twri/sdxl_prompt_styler.git

# Video
clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git
clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git

# More
clone https://github.com/pythongosssss/ComfyUI-WD14-Tagger.git
clone https://github.com/SLAPaper/ComfyUI-Image-Selector.git
clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git
