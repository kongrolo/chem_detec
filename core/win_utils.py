def check_lmstudio_status():
    """检查LM Studio服务状态"""
    import socket
    from contextlib import closing
    
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        # 检查端口是否开放
        return sock.connect_ex(('100.102.130.51', 30000)) == 0

