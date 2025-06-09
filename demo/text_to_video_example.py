#!/usr/bin/env python3
"""
文生视频示例脚本
使用 WanVideo 模型从文本描述生成视频
"""

import os
import sys
from main import ComfyUIAPI, execute_workflow


def main():
    """文生视频示例"""

    # 配置参数
    config = {
        'server': '8.130.146.185:8188',
        'workflow_path': 'workflows/text_to_video_workflow.json',
        'output_dir': './output/t2v/',
    }

    # 检查工作流文件是否存在
    if not os.path.exists(config['workflow_path']):
        print(f"❌ 工作流文件不存在: {config['workflow_path']}")
        print("请确保 image_to_video_workflow.json 文件在 workflows 目录下")
        return 1

    # 基于你的图片风格设计的文生视频提示词
    positive_prompt = """
    A beautiful anime girl with long flowing black hair and captivating brown eyes, 
    wearing an elegant black dress with a choker necklace. She has a confident and 
    alluring expression with a subtle smile.

    Scene: She is standing in an ornate vintage room with decorative elements reminiscent 
    of playing card designs. Golden ornamental patterns and baroque-style decorations 
    frame the scene, similar to a vintage playing card background.

    Animation sequence:
    - The girl gracefully moves her head and body with elegant gestures
    - Her long black hair flows naturally in a gentle breeze
    - She occasionally touches her choker or adjusts her hair with delicate movements
    - Her dress fabric moves subtly with her motions
    - She maintains eye contact with the camera with changing expressions of confidence and allure
    - Soft, warm lighting creates beautiful shadows and highlights on her face and dress
    - The camera slowly pans around her, capturing different angles
    - Background elements like floating card suits (spades) add magical atmosphere
    - The ornate decorative borders remain stable while she moves

    Style: High-quality anime art, smooth animation, cinematic lighting, 
    elegant and sophisticated mood, vintage aesthetic with modern anime style,
    playing card theme, ornate decorative elements
    """

    negative_prompt = """
    bad quality video, blurry, distorted face, deformed hands, choppy animation, 
    flickering, inconsistent lighting, low resolution, artifacts, glitches,
    bad anatomy, malformed limbs, extra fingers, missing fingers, 
    background changes, unstable elements, poor animation quality
    """

    # 参数更新
    updates = {
        # 文本提示词
        'node_49_inputs_positive_prompt': positive_prompt,
        'node_49_inputs_negative_prompt': negative_prompt,

        # 生成参数
        'node_52_inputs_steps': 15,  # 采样步数
        'node_52_inputs_cfg': 7.5,  # CFG 引导强度
        'node_52_inputs_seed': 12345,  # 随机种子

        # 视频参数
        'node_50_inputs_generation_width': 720,  # 宽度
        'node_50_inputs_generation_height': 1024,  # 高度 (适合竖版)
        'node_50_inputs_num_frames': 81,  # 帧数 (约5秒@16fps)

        # 视频输出设置
        'node_54_inputs_frame_rate': 16,  # 帧率
        'node_54_inputs_filename_prefix': 'anime_girl_t2v',
    }

    print("🎬 开始文生视频任务...")
    print(f"🎯 输出目录: {config['output_dir']}")
    print(f"📐 分辨率: {updates['node_50_inputs_generation_width']}x{updates['node_50_inputs_generation_height']}")
    print(f"🎞️  帧数: {updates['node_50_inputs_num_frames']} 帧")
    print(f"⚙️  采样步数: {updates['node_52_inputs_steps']}")
    print(f"🎛️  CFG: {updates['node_52_inputs_cfg']}")

    # 创建API客户端
    api = ComfyUIAPI(config['server'])

    try:
        # 执行工作流 (注意：文生视频不需要输入图片)
        output_file = execute_workflow(
            api=api,
            workflow_path=config['workflow_path'],
            image_path=None,  # 文生视频不需要输入图片
            updates=updates,
            output_dir=config['output_dir']
        )

        if output_file:
            print(f"\n✅ 文生视频完成!")
            print(f"📁 输出文件: {output_file}")
            return 0
        else:
            print("\n❌ 文生视频失败")
            return 1

    except Exception as e:
        print(f"\n❌ 执行过程中出错: {e}")
        return 1
    finally:
        api.close()


if __name__ == "__main__":
    exit(main())
