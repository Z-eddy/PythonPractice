import os
import requests
from urllib.parse import unquote, urlparse


def download_files_from_string(links_string, download_dir, proxy=None):
    """
    从包含多个下载链接的字符串下载文件

    参数:
        links_string: 包含多个下载链接的字符串，每行一个链接
        download_dir: 下载目录
        proxy: 代理设置，格式为:
               - SOCKS代理: "socks5://user:pass@host:port"
               - HTTP代理: "http://user:pass@host:port"
               默认为None（不使用代理）
    """
    # 创建下载目录（如果不存在）
    os.makedirs(download_dir, exist_ok=True)

    # 分割字符串为行列表
    links = links_string.strip().split('\n')

    # 设置会话对象，以便重用连接
    session = requests.Session()

    # 如果提供了代理，配置会话
    if proxy:
        session.proxies = {
            'http': proxy,
            'https': proxy
        }

    for url in links:
        url = url.strip()  # 去除前后空格
        if not url:  # 跳过空行
            continue

        try:
            # 从URL提取文件名
            parsed = urlparse(url)
            filename = unquote(os.path.basename(parsed.path))

            # 如果URL不以文件名结尾，使用默认名
            if not filename or '.' not in filename:
                filename = f"downloaded_file_{hash(url)}.tmp"

            filepath = os.path.join(download_dir, filename)

            print(f"正在下载: {url} → {filepath}")

            # 使用流式下载
            with session.get(url, stream=True) as r:
                r.raise_for_status()  # 检查请求是否成功
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:  # 过滤掉保持连接的chunk
                            f.write(chunk)

            print(f"下载完成: {filename}")

        except Exception as e:
            print(f"下载失败 [{url}]: {str(e)}")


# 示例使用
if __name__ == "__main__":
    # 示例链接字符串（每行一个URL）
    example_links = """
    https://down.zxcs.info/upload/2025/06/wdjhnxx,d2t.zip
    """

    # 不使用代理
    # download_files_from_string(example_links, R"T:\story\temp")

    # 使用SOCKS5代理
    # download_files_from_string(example_links, R"T:\story\temp", "socks5://127.0.0.1:18080")

    # 使用HTTP代理（带认证）
    download_files_from_string(example_links, R"T:\story\temp", "http://127.0.0.1:18081")

    # 下载到指定目录
    # download_files_from_string(example_links, R"T:\story\temp")