#!/usr/bin/env python3
"""
图生视频示例脚本
使用 WanVideo 模型将静态图片转换为动态视频
"""

import os
import sys
from main import ComfyUIAPI, execute_workflow


def main():
    """图生视频示例"""

    # 配置参数
    config = {
        'server': '8.130.146.185:8188',
        'workflow_path': 'workflows/image_to_video_workflow.json',
        'input_image': 'my_image.png',
        'output_dir': './output/i2v/',
    }

    # 检查文件是否存在
    if not os.path.exists(config['input_image']):
        print(f"❌ 输入图片不存在: {config['input_image']}")
        return 1

    if not os.path.exists(config['workflow_path']):
        print(f"❌ 工作流文件不存在: {config['workflow_path']}")
        print("请确保将原始的JSON配置保存为 text_to_video_workflow.json")
        return 1

    # 为这张动漫风格卡牌女孩图片定制的提示词
    positive_prompt = """
    A beautiful anime girl with long black hair and brown eyes, wearing an elegant black dress with a choker. 
    She is depicted on a vintage playing card (6 of spades) with ornate decorative borders.

    Animation sequence:
    - The girl gently tilts her head from side to side with a subtle, charming smile
    - Her long black hair flows naturally with soft, graceful movements
    - She occasionally touches her choker or adjusts her hair with delicate hand gestures
    - Her eyes blink naturally and show gentle expressions of confidence and allure
    - The dress fabric moves slightly with her body movements
    - Soft lighting creates gentle shadows and highlights on her face and dress
    - The playing card background remains stable while she moves
    - Her pose shifts slightly, showing different angles of her elegant figure

    Camera work:
    - Smooth, subtle camera movements that enhance the elegant atmosphere
    - Occasional close-ups of her expressive eyes and facial features
    - The ornate card border should remain visible throughout the animation
    - Gentle zoom in and out to emphasize her beauty and the card design

    Style: High-quality anime art style, smooth animation, elegant and sophisticated mood,
    vintage playing card aesthetic, ornate decorative elements
    """

    negative_prompt = """
    bad quality video, blurry, distorted face, deformed hands, choppy animation, 
    flickering, inconsistent lighting, background changes, card border disappearing,
    low resolution, artifacts, glitches, bad anatomy, malformed limbs
    """

    # 参数更新
    updates = {
        # 文本提示词
        'node_49_inputs_positive_prompt': positive_prompt,
        'node_49_inputs_negative_prompt': negative_prompt,

        # 生成参数
        'node_52_inputs_steps': 12,  # 采样步数
        'node_52_inputs_cfg': 6.5,  # CFG 引导强度
        'node_52_inputs_seed': 42,  # 随机种子

        # 视频参数
        'node_50_inputs_generation_width': 360,  # 宽度
        'node_50_inputs_generation_height': 480,  # 高度 (适合竖版卡牌)
        'node_50_inputs_num_frames': 81,  # 帧数 (约5秒@16fps)

        # 视频输出设置
        'node_54_inputs_frame_rate': 16,  # 帧率
        'node_54_inputs_filename_prefix': 'anime_card_girl_i2v',
    }

    print("🎬 开始图生视频任务...")
    print(f"📷 输入图片: {config['input_image']}")
    print(f"🎯 输出目录: {config['output_dir']}")
    print(f"📐 分辨率: {updates['node_50_inputs_generation_width']}x{updates['node_50_inputs_generation_height']}")
    print(f"🎞️  帧数: {updates['node_50_inputs_num_frames']} 帧")

    # 创建API客户端
    api = ComfyUIAPI(config['server'])

    try:
        # 执行工作流
        output_file = execute_workflow(
            api=api,
            workflow_path=config['workflow_path'],
            image_path=config['input_image'],
            updates=updates,
            output_dir=config['output_dir']
        )

        if output_file:
            print(f"\n✅ 图生视频完成!")
            print(f"📁 输出文件: {output_file}")
            return 0
        else:
            print("\n❌ 图生视频失败")
            return 1

    except Exception as e:
        print(f"\n❌ 执行过程中出错: {e}")
        return 1
    finally:
        api.close()


if __name__ == "__main__":
    exit(main())
