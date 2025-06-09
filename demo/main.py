import requests
import json
import time
import uuid
import os
import argparse
from typing import Optional, Dict, Any
import urllib3
from urllib.parse import urlparse

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ComfyUIAPI:
    def __init__(self, server_address="127.0.0.1:8188", timeout=30):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.timeout = timeout

        # 确保server_address格式正确
        if not server_address.startswith(('http://', 'https://')):
            self.base_url = f"http://{server_address}"
        else:
            self.base_url = server_address.rstrip('/')
            # 从URL中提取host:port
            parsed = urlparse(self.base_url)
            self.server_address = f"{parsed.hostname}:{parsed.port or 80}"

        # 创建session以复用连接
        self.session = requests.Session()
        self.session.timeout = timeout

        # 设置重试策略
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def test_connection(self) -> bool:
        """测试与ComfyUI服务器的连接"""
        try:
            print(f"测试连接到: {self.base_url}")
            response = self.session.get(f"{self.base_url}/queue", timeout=10)
            if response.status_code == 200:
                print("✅ 连接成功")
                return True
            else:
                print(f"❌ 连接失败，状态码: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {e}")
            return False
        except requests.exceptions.Timeout:
            print("❌ 连接超时")
            return False
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False

    def queue_prompt(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """提交工作流到队列"""
        try:
            p = {"prompt": prompt, "client_id": self.client_id}
            response = self.session.post(
                f"{self.base_url}/prompt",
                json=p,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"提交工作流失败: {e}")
            raise

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """获取执行历史"""
        try:
            response = self.session.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取历史失败: {e}")
            raise

    def get_queue(self) -> Dict[str, Any]:
        """获取队列状态"""
        try:
            response = self.session.get(
                f"{self.base_url}/queue",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取队列状态失败: {e}")
            raise

    def wait_for_completion(self, prompt_id: str, check_interval: int = 2) -> Dict[str, Any]:
        """等待任务完成"""
        print(f"等待任务完成，ID: {prompt_id}")
        while True:
            try:
                history = self.get_history(prompt_id)
                if prompt_id in history:
                    print("任务完成！")
                    return history[prompt_id]

                # 检查队列状态
                queue = self.get_queue()
                queue_remaining = len(queue.get('queue_running', [])) + len(queue.get('queue_pending', []))
                print(f"队列中剩余任务: {queue_remaining}")

                time.sleep(check_interval)
            except Exception as e:
                print(f"检查状态时出错: {e}")
                time.sleep(check_interval)

    def upload_image(self, image_path: str) -> bool:
        """上传图片到ComfyUI"""
        if not os.path.exists(image_path):
            print(f"图片文件不存在: {image_path}")
            return False

        # 检查文件大小
        file_size = os.path.getsize(image_path)
        print(f"图片文件大小: {file_size / 1024 / 1024:.2f} MB")

        try:
            with open(image_path, 'rb') as f:
                files = {'image': (os.path.basename(image_path), f, 'image/png')}

                print(f"正在上传到: {self.base_url}/upload/image")
                response = self.session.post(
                    f"{self.base_url}/upload/image",
                    files=files,
                    timeout=60  # 上传文件使用更长的超时时间
                )

                print(f"上传响应状态码: {response.status_code}")
                if response.status_code == 200:
                    print("✅ 图片上传成功")
                    return True
                else:
                    print(f"❌ 上传失败，状态码: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    return False

        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {e}")
            return False
        except requests.exceptions.Timeout:
            print("❌ 上传超时，请检查网络连接或尝试更小的图片")
            return False
        except Exception as e:
            print(f"❌ 上传图片失败: {e}")
            return False

    def download_output(self, filename: str, output_path: str = "./output/") -> Optional[str]:
        """下载生成的输出文件"""
        try:
            os.makedirs(output_path, exist_ok=True)

            # 构建下载URL
            url = f"{self.base_url}/view?filename={filename}&type=output"
            print(f"下载URL: {url}")

            response = self.session.get(url, timeout=120)
            response.raise_for_status()

            output_file = os.path.join(output_path, filename)
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"文件已保存到: {output_file}")
            return output_file

        except requests.exceptions.RequestException as e:
            print(f"下载文件失败: {e}")
            return None
        except Exception as e:
            print(f"下载文件时出错: {e}")
            return None

    def close(self):
        """关闭session"""
        if hasattr(self, 'session'):
            self.session.close()


def load_workflow_from_file(workflow_path: str) -> Dict[str, Any]:
    """从JSON文件加载工作流"""
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"成功加载工作流: {workflow_path}")
        return workflow
    except FileNotFoundError:
        print(f"错误: 工作流文件不存在: {workflow_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"错误: 工作流JSON格式错误: {e}")
        raise
    except Exception as e:
        print(f"错误: 加载工作流失败: {e}")
        raise


def update_workflow_parameters(
        workflow: Dict[str, Any],
        updates: Dict[str, Any]
) -> Dict[str, Any]:
    """更新工作流参数"""

    # 创建工作流副本
    updated_workflow = json.loads(json.dumps(workflow))

    for key, value in updates.items():
        if key.startswith('node_'):
            # 格式: node_42_inputs_image = "new_image.jpg"
            parts = key.split('_', 3)
            if len(parts) >= 4:
                node_id = parts[1]
                section = parts[2]  # inputs, class_type等
                param_key = parts[3]

                if node_id in updated_workflow:
                    if section not in updated_workflow[node_id]:
                        updated_workflow[node_id][section] = {}
                    updated_workflow[node_id][section][param_key] = value
                    print(f"更新节点 {node_id}.{section}.{param_key} = {value}")

    return updated_workflow


def execute_workflow(
        api: ComfyUIAPI,
        workflow_path: str,
        image_path: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None,
        output_dir: str = "./output/"
) -> Optional[str]:
    """执行工作流"""

    # 1. 测试连接
    if not api.test_connection():
        print("无法连接到ComfyUI服务器")
        return None

    # 2. 加载工作流
    print(f"加载工作流: {workflow_path}")
    workflow = load_workflow_from_file(workflow_path)

    # 3. 上传图片（如果需要）
    if image_path:
        print("正在上传图片...")
        image_filename = os.path.basename(image_path)
        if not api.upload_image(image_path):
            print("图片上传失败")
            return None

        # 自动更新LoadImage节点
        if not updates:
            updates = {}

        # 查找LoadImage节点并更新
        for node_id, node_data in workflow.items():
            if node_data.get('class_type') == 'LoadImage':
                updates[f'node_{node_id}_inputs_image'] = image_filename
                break

    # 4. 更新工作流参数
    if updates:
        print("更新工作流参数...")
        workflow = update_workflow_parameters(workflow, updates)

    # 5. 提交任务
    print("提交生成任务...")
    try:
        result = api.queue_prompt(workflow)

        if 'prompt_id' not in result:
            print(f"提交任务失败: {result}")
            return None

        prompt_id = result['prompt_id']
        print(f"任务已提交，ID: {prompt_id}")

        # 6. 等待完成
        history = api.wait_for_completion(prompt_id)

        # 7. 获取生成的文件
        output_files = []
        for node_id in history.get('outputs', {}):
            node_output = history['outputs'][node_id]

            # 检查各种输出类型
            for output_type in ['images', 'gifs', 'videos']:
                if output_type in node_output:
                    for file_info in node_output[output_type]:
                        filename = file_info['filename']
                        output_path = api.download_output(filename, output_dir)
                        if output_path:
                            output_files.append(output_path)

        if output_files:
            print(f"生成了 {len(output_files)} 个文件")
            return output_files[0]  # 返回第一个文件
        else:
            print("未找到生成的文件")
            return None

    except Exception as e:
        print(f"执行工作流时出错: {e}")
        return None


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="ComfyUI API 客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py -w workflow.json -i image.jpg --update node_49_inputs_positive_prompt="A woman smiling"
  python main.py -w workflow.json --server 192.168.1.100:8188 --update node_52_inputs_steps=20
        """
    )

    # 必需参数
    parser.add_argument('-w', '--workflow', required=True,
                        help='工作流JSON文件路径')

    # 可选参数
    parser.add_argument('-i', '--image',
                        help='输入图片路径（如果工作流需要）')

    # 服务器配置
    parser.add_argument('--server', default='127.0.0.1:8188',
                        help='ComfyUI服务器地址 (默认: 127.0.0.1:8188)')
    parser.add_argument('--timeout', type=int, default=30,
                        help='请求超时时间(秒) (默认: 30)')

    # 参数更新
    parser.add_argument('--update', action='append',
                        help='更新工作流参数，格式: node_ID_section_key=value')

    # 输出配置
    parser.add_argument('-o', '--output', default='./output/',
                        help='输出目录 (默认: ./output/)')

    # 其他选项
    parser.add_argument('--verbose', action='store_true',
                        help='显示详细信息')
    parser.add_argument('--test-only', action='store_true',
                        help='仅测试连接，不执行生成')
    parser.add_argument('--dry-run', action='store_true',
                        help='显示更新后的工作流，不执行')

    return parser.parse_args()


def parse_updates(update_list: Optional[list]) -> Dict[str, Any]:
    """解析更新参数"""
    updates = {}
    if update_list:
        for update in update_list:
            if '=' in update:
                key, value = update.split('=', 1)
                # 尝试转换数据类型
                try:
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    elif '.' in value and value.replace('.', '').replace('-', '').isdigit():
                        value = float(value)
                except:
                    pass  # 保持字符串类型
                updates[key] = value
    return updates


def main():
    """主函数"""
    args = parse_arguments()

    # 验证文件存在
    if not os.path.exists(args.workflow):
        print(f"错误: 工作流文件不存在: {args.workflow}")
        return 1

    if args.image and not os.path.exists(args.image):
        print(f"错误: 图片文件不存在: {args.image}")
        return 1

    # 解析更新参数
    updates = parse_updates(args.update)

    # 显示配置信息
    if args.verbose:
        print("=== 配置信息 ===")
        print(f"工作流文件: {args.workflow}")
        print(f"服务器地址: {args.server}")
        if args.image: print(f"输入图片: {args.image}")
        print(f"超时时间: {args.timeout}秒")
        if updates: print(f"参数更新: {updates}")
        print(f"输出目录: {args.output}")
        print("================\n")

    # Dry run模式
    if args.dry_run:
        try:
            workflow = load_workflow_from_file(args.workflow)
            if updates:
                workflow = update_workflow_parameters(workflow, updates)
            print("=== 更新后的工作流 ===")
            print(json.dumps(workflow, indent=2, ensure_ascii=False))
            return 0
        except Exception as e:
            print(f"Dry run失败: {e}")
            return 1

    # 初始化API客户端
    try:
        api = ComfyUIAPI(args.server, timeout=args.timeout)
        print(f"连接到ComfyUI服务器: {args.server}")

        # 仅测试连接
        if args.test_only:
            if api.test_connection():
                print("✅ 连接测试成功")
                return 0
            else:
                print("❌ 连接测试失败")
                return 1

    except Exception as e:
        print(f"初始化API客户端失败: {e}")
        return 1

    # 执行工作流
    try:
        output_file = execute_workflow(
            api=api,
            workflow_path=args.workflow,
            image_path=args.image,
            updates=updates,
            output_dir=args.output
        )

        if output_file:
            print(f"\n✅ 任务执行成功！")
            print(f"📁 输出文件: {output_file}")
            return 0
        else:
            print("\n❌ 任务执行失败")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        return 1
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        return 1
    finally:
        # 清理资源
        api.close()


if __name__ == "__main__":
    exit(main())
